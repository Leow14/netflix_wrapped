import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime
import statistics as sts
from src.data_cleaning import limpar_titulo, converting_timedelta, convert_director, new_check_kids, converting_keywords_columns
from src.dummy_generator import dummy_genres, dummy_media_type, dummy_origin_country, dummy_profile
from src.tmdb_search import get_tmdb_id, tmdb_search
from src.features import calcular_engagement, perfil_principal, perfil_percentual, classify_period
from src.constants import GENRES_MAP, DAY_NAMES, MONTH_NAMES, REGRAS, PROCESSED_DATA_PATH, RAW_DATA_PATH, TIME_DELTA_COLUMNS, THUMBS_NOTA_CONVERSION_MAP
from src.power_bi import explode_countries, explode_director, explode_genres
from src.kmeans import CLUSTER_FEATURES

tempo_inicio = time.time()
print(f"Iniciando script...\n{datetime.now()}")

# Criando bases de acordo com os dados crus da netflix
viewing_activity                    = pd.read_csv(f"{RAW_DATA_PATH }/CONTENT_INTERACTION/ViewingActivity.csv")
my_list                             = pd.read_csv(f"{RAW_DATA_PATH }/CONTENT_INTERACTION/MyList.csv")
ratings                             = pd.read_csv(f"{RAW_DATA_PATH }/CONTENT_INTERACTION/Ratings.csv")
devices                             = pd.read_csv(f"{RAW_DATA_PATH }/DEVICES/Devices.csv")
avatar_history                      = pd.read_csv(f"{RAW_DATA_PATH }/PROFILES/AvatarHistory.csv")
profiles                            = pd.read_csv(f"{RAW_DATA_PATH }/PROFILES/Profiles.csv")

titulos_adicionar                   = pd.read_csv(f'data/processed/titulos_a_adicionar_new.csv', sep=";")
#titulos_adicionar['CleanTitle']    = titulos_adicionar['CleanTitle'].apply(convert_text_csv)
titulos_adicionar['nota']           = titulos_adicionar['nota'].apply(lambda x: x/10)
titulos_selecionados                = titulos_adicionar.iloc[:,:-1]

#print(titulos_adicionar.head(5))
print("Bases da netflix carregadas")

# Tratamentos de dados inicia aqui
viewing_activity['Start Time']      = pd.to_datetime(viewing_activity['Start Time'], utc=True)
viewing_activity['Duration']        = pd.to_timedelta(viewing_activity['Duration'])

viewing_activity["period_of_day"] = viewing_activity["Start Time"].dt.hour.apply(classify_period)
viewing_activity.to_csv(f"{RAW_DATA_PATH }/CONTENT_INTERACTION/ViewingActivity.csv")

# Supplemental Video Type = Null são atividades que não são trailers, teasers, etc
viewing_activity                    = viewing_activity[viewing_activity['Supplemental Video Type'].isna()].copy() 
viewing_activity["dia_da_semana"]   = viewing_activity["Start Time"].dt.dayofweek
viewing_activity["mes_do_ano"]      = viewing_activity["Start Time"].dt.month

# Criando colunas auxiliares para a sazonalidade por horário
hora = viewing_activity["Start Time"].dt.hour
viewing_activity.loc[(hora >= 5)    & (hora < 12), "morning"]   = viewing_activity["Duration"]
viewing_activity.loc[(hora >= 12)   & (hora < 18), "afternoon"] = viewing_activity["Duration"]
viewing_activity.loc[(hora >= 18)   & (hora < 24), "night"]     = viewing_activity["Duration"]
viewing_activity.loc[(hora >= 0)    & (hora < 5),  "dawn"]      = viewing_activity["Duration"]


viewing_activity['total_check'] = (  
    viewing_activity['dawn']      +
    viewing_activity['morning']   +  
    viewing_activity['afternoon'] +
    viewing_activity['night']
)

# Mapeando thumbs e transformando em notas
ratings["Thumbs Value"] = ratings["Thumbs Value"].map(THUMBS_NOTA_CONVERSION_MAP)


# Listando todos os perfis de usuários
profile_list = viewing_activity["Profile Name"].dropna().unique()

# Variável global com a lista de nomes do perfil
profile_list = [name.lower().replace(" ", "_") for name in profile_list]
#print(profile_list)
PROFILE_LIST = profile_list

for day in range(7):
    column_name = f"{DAY_NAMES[day]}_views"
    viewing_activity[column_name] = (viewing_activity["dia_da_semana"] == day).astype(int)

for month in range(1, 13):
    column_name = f"{MONTH_NAMES[month-1]}_views"
    viewing_activity[column_name] = (viewing_activity["mes_do_ano"] == month).astype(int)

# Aplicando funções de tratamento de dados aos títulos
ratings['CleanTitle']           = ratings["Title Name"].apply(limpar_titulo)
viewing_activity["CleanTitle"]  = viewing_activity["Title"].apply(limpar_titulo)
my_list["CleanTitle"]           = my_list["Title Name"].apply(limpar_titulo)
my_list_titles                  = set(my_list["CleanTitle"])
my_ratings_titles               = set(ratings["CleanTitle"])

# Deixando apenas o último rating
ratings = ratings.drop_duplicates(subset=["CleanTitle"], keep='last')

# Criando a unique titles. Uma base que vai agrupar a somatória de tempo assistido pelos títulos.
unique_titles = (
    viewing_activity
    .groupby(['CleanTitle'], as_index=False)
    .agg(WatchedTime        = ('Duration', 'sum'),
        last_watched_date   = ("Start Time", "max") ,
        first_watched_date  = ("Start Time", "min") ,
        )
    .sort_values('WatchedTime', ascending=False)
)

PROFILES_NAMES_DF = pd.DataFrame(profiles["Profile Name"].unique(), columns=['Profile Name'])
PROFILES_NAMES_DF.to_csv('data/processed/profile_name.csv', index=False, encoding="utf-8-sig")
print(PROFILES_NAMES_DF)


# Unique title per profile é semelhante a base anterior. Mas a diferença é que filtra os títulos com base nos perfis.
unique_titles_per_profile = (
    viewing_activity
    .groupby(['CleanTitle', 'Profile Name'], as_index=False)
    .agg(**REGRAS) # Descompactando a constante REGRAS.
    .sort_values('WatchedTime', ascending=False)
)


unified_base = pd.concat(
    [unique_titles_per_profile, titulos_selecionados],
    join='outer', ignore_index=True
    ).drop_duplicates(subset=['CleanTitle'], keep='first')

#print(titulos_selecionados.columns)

print("Carregando busca por ID, aguarde...")
tmdb_base = pd.DataFrame({"netflix_title"    : pd.Series(dtype='str'),
                          "title"            : pd.Series(dtype='str'),
                          "genre_ids"        : pd.Series(dtype='object'),
                          "poster_path"      : pd.Series(dtype='str'),
                          "media_type"       : pd.Series(dtype='str'),
                          "popularity"       : pd.Series(dtype='float64'),  
                          "age_of_title"     : pd.Series(dtype='int64'),
                          "vote_average"     : pd.Series(dtype='float64'),
                          "vote_count"       : pd.Series(dtype='int64'),
                          "run_time"         : pd.Series(dtype='float64'),
                          "num_seasons"      : pd.Series(dtype='int64'),
                          "origin_country"   : pd.Series(dtype='object'),
                          "keywords"         : pd.Series(dtype='object'),
                          "director"         : pd.Series(dtype='object'),
                          "content_rating"   : pd.Series(dtype='str'),
                          "is_natalino"      : pd.Series(dtype='int64'),
                          "is_super_heroi"   : pd.Series(dtype='int64'),
                          "is_dorama"        : pd.Series(dtype='int64'),
                          "is_kids"          : pd.Series(dtype='int64'),
                          "is_dystopian"     : pd.Series(dtype='int64'),
                          "is_based_on_book" : pd.Series(dtype='int64'),
                          "is_anime"         : pd.Series(dtype='int64')
                          })

#print(titulos_selecionados.columns)

c = 1
for title in unified_base['CleanTitle']:
    title, tmdb_id, media_type = get_tmdb_id(title)
    print(f'[{c}/{len(unified_base)}] {title}')
    nova_linha = tmdb_search(title, tmdb_id, media_type)
    tmdb_base = pd.concat([tmdb_base, pd.DataFrame([nova_linha])], ignore_index=True)
    c += 1

# Merge com a base de dados da netflix
final_df = unified_base.merge( 
    tmdb_base,
    left_on='CleanTitle',
    right_on='netflix_title',
    how='left'
)

for col in TIME_DELTA_COLUMNS:
    if col not in final_df.columns:
        continue
    final_df[col] = final_df[col].apply(converting_timedelta)

# Criando um set com um país de cada
country_set = set()

for origin_country_list in final_df["origin_country"]:
    if origin_country_list:
        for origin_country_name in origin_country_list:
            if origin_country_name:
                country_set.add(origin_country_name)

# Incluindo o valor das notas dadas pelos usuários
notas_unified = pd.concat([
    ratings[['CleanTitle', 'Thumbs Value']].rename(columns={'Thumbs Value' : 'nota'}),
    titulos_adicionar[['CleanTitle', 'nota']].rename(columns={'notas': 'nota'})
    ], ignore_index=True).drop_duplicates(keep='first')

final_df = final_df.merge(
    notas_unified[["CleanTitle", "nota"]],
    on="CleanTitle",
    how="left"
)

nota_list        = list(final_df["nota"])
nota_list        = [x for x in nota_list if pd.notna(x)]
nota_mean_value  = float(sts.mean(nota_list))
final_df["nota"]                     = final_df["nota"].fillna(nota_mean_value)

print(type(final_df["WatchedTime"]))
print(final_df["WatchedTime"])
print("Até aqui deu certo")

# Incluindo as colunas day_between e avg_duration_per_sesion
final_df["avg_duration_per_session"] = final_df["WatchedTime"] / final_df["count_per_title"]
final_df["day_between"]              = final_df["last_watched_date"] - final_df["first_watched_date"]
final_df["is_tv"]                    = final_df["media_type"].apply(dummy_media_type)
final_df["is_in_list"]               = final_df["CleanTitle"].apply(lambda x: 1 if x in my_list_titles else 0)
final_df["has_rated"]                = final_df["CleanTitle"].apply(lambda x: 1 if x in my_ratings_titles else 0)
final_df['engagement_score']         = final_df.apply(calcular_engagement, axis=1, nota_mean=nota_mean_value)
final_df["is_kids"]                  = final_df.apply(lambda row: new_check_kids(row["keywords"],row["content_rating"]) if 
                                     ("keywords" in row and "content_rating" in row) else 0,axis=1)
final_df["content_rating"]           = pd.to_numeric(final_df["content_rating"], errors="coerce").fillna(0)
final_df["content_rating"]           = pd.to_numeric(final_df["content_rating"], errors="coerce").fillna(0)
final_df["is_mature"]                = (final_df["content_rating"] >= 3).astype(int)
final_df["director"]                 = final_df["director"].apply(convert_director)

# TODO renomear colunas para deixar todas em snake case



# ! Criando a title_dim
dim_titles = (
final_df.drop_duplicates(subset=["title"])
[["CleanTitle","title","media_type","popularity"]]
.reset_index(drop=True)
)
dim_titles.to_csv("data/processed/dim_titles.csv", index=False, encoding="utf-8-sig")
explode_df                            = final_df.copy()
explode_df["watched_time"]            = explode_df["WatchedTime"].dt.total_seconds()
explode_df["watched_time_dawn"]       = explode_df["watched_time_dawn"].dt.total_seconds()
explode_df["watched_time_morning"]    = explode_df["watched_time_morning"].dt.total_seconds()
explode_df["watched_time_afternoon"]  = explode_df["watched_time_afternoon"].dt.total_seconds()
explode_df["watched_time_night"]      = explode_df["watched_time_night"].dt.total_seconds()


df_genres    = explode_genres(explode_df)
df_countries = explode_countries(explode_df)
df_directors = explode_director(explode_df)


power_all    = final_df.copy()
power_all.to_csv("data/processed/power_all.csv", index=False, encoding="utf-8-sig")
df_genres.to_csv("data/processed/dim_genres.csv", index=False, encoding="utf-8-sig")
df_countries.to_csv("data/processed/dim_countries.csv", index=False, encoding="utf-8-sig")
df_directors.to_csv("data/processed/dim_directors.csv", index=False, encoding="utf-8-sig")

explode_df.to_csv("data/processed/main_df.csv", index=False, encoding="utf-8-sig")


# Incluindo colunas restantes
final_df                             = dummy_genres(final_df, GENRES_MAP)
final_df                             = dummy_origin_country(final_df, country_set)
final_df                             = dummy_profile(final_df, profile_list)
final_df                             = converting_keywords_columns(final_df)

df_ml = final_df.copy()

# Salvando CSV.
df_ml.to_csv(PROCESSED_DATA_PATH, index=False, encoding="utf-8-sig")

icons = [
    "perfil_vermelho.png",
    "perfil_azul.png",
    "perfil_verde.png",
    "perfil_amarelo.png",
    "perfil_rosa.png"
]

profiles_df_icons = pd.read_csv("data/processed/profile_name.csv", encoding="utf-8-sig")

profiles_df_icons["avatar_name"] = [
    icons[i % len(icons)] for i in range(len(profiles_df_icons))
]

profiles_df_icons["avatar_url"] = (
    "design/Icons/" + profiles_df_icons["avatar_name"]
)

profiles_df_icons.to_csv("data/processed/perfis.csv", index=False, encoding="utf-8-sig")

wrapped = final_df[CLUSTER_FEATURES]
wrapped["WatchedTime"] = pd.to_timedelta(wrapped["WatchedTime"], errors="coerce")
wrapped["WatchedTime"] = wrapped["WatchedTime"].dt.total_seconds() / 60

user_profiles = wrapped.groupby("Profile Name").mean()
profile_names = user_profiles.index.tolist()
print(profile_names)


user_profiles["perfil_percentual"] = user_profiles.apply(perfil_percentual, axis=1)
df_percentual = user_profiles["perfil_percentual"].apply(pd.Series)
user_profiles = pd.concat([user_profiles, df_percentual], axis=1)
user_profiles = user_profiles.drop(columns=["perfil_percentual"])

user_profiles["perfil_principal"] = user_profiles.apply(perfil_principal, axis=1)
user_profiles = user_profiles.reset_index()
user_profiles.to_csv("data/processed/perfis_finais.csv", index=False, encoding="utf-8-sig")

tempo_final     = time.time()
duracao_runtime = (tempo_final - tempo_inicio)/60
print(f"Tudo certo! verifique o CSV. runtime : {duracao_runtime:.2f}")
print(f"Aqui estão as colunas finais: {final_df.columns}\n{datetime.now()}")

