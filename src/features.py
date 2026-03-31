
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from src.constants import PROFILE_LIST

import pandas as pd
def calcular_engagement(row, nota_mean=6.5):

    minutos_assistidos = row["WatchedTime"].total_seconds() / 60 # 80

    nota = row["nota"] # 60
    if pd.isna(nota):
        nota = nota_mean
    nota = float(nota)

    run_time = row["run_time"]
    if row["is_tv"] == 1:

        if isinstance(run_time, list):
            run_time = run_time[0] if run_time else 40

        if pd.isna(run_time) or run_time == 0:
            run_time = 40

        title_duration = run_time * 3

        total = minutos_assistidos / title_duration if title_duration > 0 else 0
        total = min(total, 1)

        score = (
            total * 5 +
            (nota / 10) * 5
        )

    else:

        if pd.isna(run_time) or run_time == 0:
            run_time = 80

        score_time = minutos_assistidos / run_time
        score_time = min(score_time, 1)

        score = (
            score_time * 5 +
            (nota / 10) * 5
        )
        
    return score

FEATURES_CONTEUDO = [
    # Colunas base
    "popularity", "age_of_title", "vote_average",
    "num_seasons", "director", "content_rating", "is_mature",

    # Target
    'title',

    # Gêneros
    "is_action", "is_adventure", "is_animation", "is_comedy", "is_crime",
    "is_documentary", "is_drama", "is_family", "is_fantasy", "is_history",
    "is_horror", "is_music", "is_mystery", "is_romance", "is_science_fiction",
    "is_tv_movie", "is_thriller", "is_war", "is_western",
    "is_action_e_adventure", "is_news", "is_reality", "is_sci-fi_e_fantasy",
    "is_soap", "is_talk", "is_war_e_politics",
    
    # Perfis
    "léo", "anas", "jose", "Profile Name",
    
    # Países
    "is_it", "is_kr", "is_lu", "is_es", "is_mw", "is_br", "is_ch", "is_no",
    "is_de", "is_ie", "is_se", "is_th", "is_tr", "is_co", "is_fr", "is_in",
    "is_nl", "is_is", "is_us", "is_dk", "is_au", "is_ar", "is_ca", "is_jp",
    "is_gb", "is_fi", "is_cn", "is_pl", "is_mx", "is_ph", "is_hk",

    # Assistencial
    "is_tv", "is_in_list", "has_rated",
    
    # Key_words
    "1970s", "1980s", "adventure", "alien", "amused",
    "animals", "anime", "anthology", "based_on_comic", "based_on_manga",
    "based_on_novel_or_book", "based_on_true_story", "biography", "cartoon",
    "christmas", "coming_of_age", "competition", "corruption",
    "dark_comedy", "death", "demon", "detective", "dog", "dramatic",
    "drugs", "dystopia", "family", "family_relationships", "fbi",
    "female_protagonist", "friends", "friendship", "gay_theme",
    "ghost", "high_school", "holiday", "horror",
    "husband_wife_relationship", "infidelity", "investigation",
    "kidnapping", "lgbt", "london__england", "los_angeles__california",
    "love", "love_triangle", "magic", "marriage", "martial_arts", "mecha",
    "miniseries", "monster", "murder", "musical", "new_york_city",
    "parent_child_relationship", "police", "politics", "prison",
    "revenge", "road_trip", "romance", "romantic", "romcom", "school",
    "sequel", "serial_killer", "short_film", "shounen",
    "sibling_relationship", "sitcom", "slice_of_life", "small_town",
    "sports", "stand-up_comedy", "super_power", "superhero", "supernatural",
    "survival", "suspenseful", "teenager", "time_travel", "true_crime",
    "villain", "woman_director", "world_war_ii"
]


TARGET = 'engagement_score'  
ID_COL = 'title'

def selecionando_features_finais(df):
    # Filtrar apenas as colunas que existem no DF (evita erro ase alguma sumiu)
    colunas_existentes = [c for c in FEATURES_CONTEUDO if c in df.columns]
    df_final = df[colunas_existentes].copy()

    return df_final[colunas_existentes].fillna(0)

def read_csv_safe(path):
    try:
        return pd.read_csv(path, encoding="utf-8")
    except:
        return pd.read_csv(path, encoding="latin-1")
    
def fix_encoding(text):
    if isinstance(text, str):
        try:
            return text.encode("latin-1").decode("utf-8")
        except:
            return text
    return text

def perfil_percentual(row):
    if row["WatchedTime"] < 50:
        return "Vazio"
    scores = {
        "Otaku"       : row["is_anime"] + row["is_jp"],
        "Dorameiro"   : row["is_dorama"] + row["is_kr"],
        "Ação"        : row["is_action"] + row["is_adventure"],
        "Super-Herói" : row["is_super_heroi"] * 2,
        "Suspense"    : row["is_horror"] + row["is_thriller"],
        "Documentário": row["is_documentary"] + row["is_history"],
        "Comédia"     : row["is_comedy"] * 2,
        "Kids"        : row["is_animation"] + row["is_family"],
    }
    
    total = sum(scores.values()) + 1e-6

    return {k: round(v/total, 2) for k, v in scores.items()}


def perfil_principal(row):
    if row["WatchedTime"] < 50:
        return "Vazio"
    scores = {
        "Otaku"       : row["is_anime"] + row["is_jp"],
        "Dorameiro"   : row["is_dorama"] + row["is_kr"],
        "Ação"        : row["is_action"] + row["is_adventure"],
        "Super-Herói" : row["is_super_heroi"] * 2,
        "Suspense"    : row["is_horror"] + row["is_thriller"],
        "Documentário": row["is_documentary"] + row["is_history"],
        "Comédia"     : row["is_comedy"] * 2,
        "Kids"        : row["is_animation"] + row["is_family"],
    }

    return max(scores, key=scores.get)

def classify_period(hour):
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 18:
        return "Afternoon"
    elif 18 <= hour < 24:
        return "Night"
    else:
        return "Dawn"