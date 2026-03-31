import pandas as pd
import os

from dotenv import load_dotenv

# Arquivo de constantes. Aqui defino variáveis globais para usar em diversas partes do código. O nome da variável é auto-explicativo.

load_dotenv

GENRES_MAP = {28: 'Action', 12: 'Adventure', 16: 'Animation', 35: 'Comedy', 80: 'Crime', 
99: 'Documentary', 18: 'Drama', 10751: 'Family', 14: 'Fantasy', 36: 'History', 
27: 'Horror', 10402: 'Music', 9648: 'Mystery', 10749: 'Romance', 878: 'Science Fiction',
10770: 'TV Movie', 53: 'Thriller', 10752: 'War', 37: 'Western', 10759: 
'Action & Adventure', 10762: 'Kids', 10763: 'News', 10764: 'Reality', 10765: 
'Sci-Fi & Fantasy', 10766: 'Soap', 10767: 'Talk', 10768: 'War & Politics'}



SUPLEMENTAL_VIDEO_TYPE = [
    "CINEMAGRAPH",
    "HOOK",
    "PREVIEW",
    "PROMOTIONAL",
    "RECAP",
    "TEASER_TRAILER",
    "TRAILER",
    "TUTORIAL",
    ""
]


MOVIES_TO_BE_CLEARED = {"sandman"  : "sandman", 
                        "wandinha" : "wednesday",
                        "sereias"  : "Sirens"}


DAY_NAMES = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]
MONTH_NAMES = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]

# Regras para o merge na unique_titles_per_profile com a viewing_activity.
REGRAS = {
    "WatchedTime" : ('Duration', 'sum'),
    "watched_time_dawn" : ('dawn', 'sum'),
    "watched_time_morning" : ('morning', 'sum'),
    "watched_time_afternoon" : ('afternoon', 'sum'),
    "watched_time_night": ('night', 'sum'),
    "count_per_title": ('CleanTitle', 'count'),
    "last_watched_date": ("Start Time", "max") ,
    "first_watched_date": ("Start Time", "min")
}


for day in DAY_NAMES:
    REGRAS[f"{day}_views"] = (f'{day}_views', 'sum')


for month in MONTH_NAMES:
    REGRAS[f"{month}_views"] = (f'{month}_views', 'sum')


ANO_ATUAL = pd.Timestamp.today().year


# Keys das APIs
TMDB_KEY = os.getenv("TMDB_KEY")


# URL das APIs
TMDB_URL = "https://api.themoviedb.org/3"


# Caminho dos dados pré-processados
PROCESSED_DATA_PATH = "data/processed/final_df.csv"
KEGGLE_DATA_PATH = "data/processed/keggle_tmdb_processed.csv"


RAW_DATA_PATH = "data/raw/Main/"


COLUNAS_PARA_DROPAR = [  
    # Colunas auxiliares
    "CleanTitle", "netflix_title", "genre_ids", "media_type", "Profile Name", "WatchedTime"
    # Sazonalidade - período do dia
    'watched_time_dawn', 'watched_time_morning', 'watched_time_afternoon', 'watched_time_night',
    # Sazonalidade - dias da semana  
    'seg_views', 'ter_views', 'qua_views', 'qui_views', 'sex_views', 'sab_views', 'dom_views',
    # Sazonalidade - meses  
    'jan_views', 'fev_views', 'mar_views', 'abr_views', 'mai_views', 'jun_views',
    'jul_views', 'ago_views', 'set_views', 'out_views', 'nov_views', 'dez_views',
    # Datas e colunas auxiliares
    'last_watched_date', 'first_watched_date',
    'release_date', 'age_of_work', 'origin_country', 'avg_duration_per_session',
    # Mais colunas de países
    'is_it', 'is_cn', 'is_hu', 'is_pl', 'is_in', 'is_se', 'is_mx', 'is_no', 'is_fi', 'is_th', 'is_nl', 'is_tr', 'is_lu', 'is_is', 'is_au', 'is_dk', 'is_ar', 'is_co',
    # Colunas que não serão utilizadas para as métricas do ml
    'is_natalino', 'is_super_heroi', 'day_between',
    # Colunas redundantes de gêneros
     'is_action_e_adventure', 'is_war_e_politics','is_sci-fi_e_fantasy',

]

DONTS = ['(trailer)', '(minissérie)', '(temporada)', '(season)', '(ep)', '(episodio)', '(episódio)', '(episode)','(clipe)', '(clip)', '(teaser)', 'trailer' , 'minissérie',  'temporada', 'season', 'episode', 'episódio', 'episodio', 'clipe', 'clip', 'teaser']


FEATURES_A_TRATAR = ['popularity', 'vote_average', 'run_time', 'release_year', 'engagement_score', 'Thumbs Value', 'peso_engajamento']


TIME_DELTA_COLUMNS = [  
    "WatchedTime",
    "watched_time_dawn",
    "watched_time_morning",
    "watched_time_afternoon",
    "watched_time_night",
    "last_watched_date",
    "first_watched_date"
]

PROFILE_LIST = ()

profiles = pd.read_csv(f"{RAW_DATA_PATH }/PROFILES/Profiles.csv")
PROFILES_NAMES_DF = pd.DataFrame(profiles["Profile Name"].unique(), columns=['Profile Name'])
PROFILES_NAMES_DF.to_csv('data/processed/profile_name.csv', index=False)

THUMBS_NOTA_CONVERSION_MAP = {
    0 : 0,
    1 : 3.5,
    2 : 7,
    3 : 10
}

CLUSTER_DESCRIPTION_MAP = {
        "terror"      : "Você não assiste filmes… você enfrenta eles. Entre sustos, gritos e monstros, você tá sempre pronto pra mais um pesadelo. Se tem sangue, tensão e plot twist macabro, é sua zona de conforto.",
        "otaku"       : "Seu coração bate em japonês. Entre animes, mundos fantásticos e personagens icônicos, você já viveu mais aventuras que muito protagonista. Provavelmente já falou “isso me lembra um anime”." ,
        "dorameiro"   : "Romance intenso, olhares demorados e trilhas emocionantes definem seu estilo. Você sabe que um bom dorama resolve qualquer dia ruim. E sim… você já sofreu por personagem fictício.",
        "cult"        : "Você não assiste qualquer coisa, você aprecia cinema. Roteiros profundos, direção impecável e notas altas são seu território. Provavelmente já disse “esse filme é uma obra”.",
        "ampulheta"   : "Você viaja no tempo sem sair do sofá. Clássicos, relíquias e filmes antigos fazem parte da sua rotina. Enquanto o mundo corre, você revisita o que realmente marcou época.",
        "super-heroi" : "Explosões, poderes e batalhas épicas? Pode dar play. Você acompanha heróis como se fossem velhos amigos. No fundo, ainda acredita que alguém pode salvar o mundo.",
        "eclético"    : "Você não tem um gosto… você tem todos. De anime a documentário, de romance a ação, tudo entra na sua fila. Seu algoritmo interno é: “parece interessante? bora”.",
        "vazio"       : "Calma… você ainda tá aquecendo. Poucos títulos, pouca atividade, mas todo mundo começa de algum lugar. Seu perfil é um livro em branco esperando boas histórias.",
        "kids"        : "Leve, divertido e cheio de nostalgia. Você curte histórias simples, personagens carismáticos e aquele conforto de algo gostoso de assistir. Às vezes, ser leve é tudo."
}