import pandas as pd
from src.dummy_generator import dummy_genres, dummy_media_type, dummy_origin_country, dummy_profile
from src.constants import TIME_DELTA_COLUMNS, GENRES_MAP, ANO_ATUAL, PROFILE_LIST, COLUNAS_PARA_DROPAR
from src.data_cleaning import converting_timedelta, new_check_kids, is_latin, convert_director, converting_keywords_columns
from src.features import calcular_engagement
import time
import ast
from datetime import datetime

tempo_inicial = time.time()
keggle = pd.read_csv('data/processed/keggle_tmdb.csv')
keggle = keggle[keggle['title'].apply(is_latin)].reset_index(drop=True)

if "age_of_title" not in keggle.columns:  
    keggle["release_date"] = pd.to_datetime(keggle["release_date"], utc=True, errors="coerce")  
    keggle["age_of_title"] = ANO_ATUAL - keggle["release_date"].dt.year

for col in TIME_DELTA_COLUMNS:
    if col not in keggle.columns:
        continue
    keggle[col] = keggle[col].apply(converting_timedelta)

country_set = set()

for origin_country_list in keggle["origin_country"]:
    if not isinstance(origin_country_list, str):
        continue
    try:
        real_country_list = ast.literal_eval(origin_country_list)
        if real_country_list:
            for origin_country_name in real_country_list:
                if origin_country_name:
                    country_set.add(origin_country_name)
    except (ValueError, SyntaxError):
        country_set.add(origin_country_list.strip())

# Incluindo colunas restantes
keggle                     = dummy_genres(keggle, GENRES_MAP)
keggle                     = dummy_origin_country(keggle, country_set)
keggle["is_tv"]            = keggle["media_type"].apply(dummy_media_type)
keggle["is_in_list"]       = 0  
keggle["has_rated"]        = 0  
keggle["engagement_score"] = 0
keggle["is_kids"]          = keggle.apply(lambda row: new_check_kids(row["keywords"], 
                                                                     row["content_rating"]) if 
                                                                     ("keywords" in row and "content_rating" in row) else 0,axis=1)
keggle["director"]         = keggle["director"].apply(convert_director)
keggle                     = converting_keywords_columns(keggle)

df_ml = keggle.copy()

# Salvando CSV.
df_ml.to_csv(f'data/processed/keggle_tmdb_processed.csv', index=False, encoding="utf-8-sig")

tempo_final = time.time()
duracao_runtime = (tempo_final - tempo_inicial)/60
print(f"Tudo certo! verifique o CSV. runtime : {duracao_runtime:.2f}")
print(f"Aqui estão as colunas finais: {keggle.columns}\n{datetime.now()}")