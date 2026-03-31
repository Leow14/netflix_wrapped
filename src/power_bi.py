import ast
from src.data_cleaning import DIRECTORS_MAP
from src.constants import GENRES_MAP

directors_map = DIRECTORS_MAP

def convert_to_list(x):
        if isinstance(x, list):
            return x
        if isinstance(x, str):
            try:
                return ast.literal_eval(x)
            except:
                return []
        return []


def explode_countries(df):
    # Checa se é uma lista
    df_countries = df[["CleanTitle", "origin_country"]].copy()
    df_countries["origin_country"] = df_countries["origin_country"].apply(convert_to_list)
    
    # Dá o explode
    df_countries = df_countries.explode("origin_country")
    df_countries = df_countries.dropna(subset=["origin_country"])
    df_countries = df_countries.rename(columns={"origin_country": "country"})


    return df_countries.drop_duplicates().reset_index(drop=True)


def explode_genres(df):
    
    df_genres = df[["CleanTitle", "genre_ids"]].copy()
    df_genres["genre_ids"] = df_genres["genre_ids"].apply(convert_to_list)

    df_genres = df_genres.explode("genre_ids")
    df_genres = df_genres.dropna(subset=["genre_ids"])
    
    df_genres["genre"] = df_genres["genre_ids"].map(GENRES_MAP)
    df_genres["genre"] = df_genres["genre"].fillna(df_genres["genre_ids"])
    df_genres = df_genres.drop(columns=["genre_ids"])
    
    return df_genres.drop_duplicates().reset_index(drop=True)

def explode_director(df):

    df_director = df[["CleanTitle", "director"]].copy()
    df_director["director"] = df_director["director"].apply(convert_to_list)

    df_director = df_director.explode("director")
    df_director = df_director.dropna(subset=["director"])

    df_director["director"] = df_director["director"].map(DIRECTORS_MAP)
    df_director["director"] = df_director["director"].fillna(df_director["director"])

    return df_director.drop_duplicates().reset_index(drop=True)