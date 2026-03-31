
import ast

def dummy_profile(df, profile_list):
    for name in profile_list:
        column_name = name.lower().replace(" ", "_")
        df[column_name] = (df["Profile Name"].str.lower().str.replace(" ", "_") == column_name).astype(int)
    return df


def dummy_genres(df, genres_dict):
    true_genres_id = df['genre_ids'].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else (x if isinstance(x, list) else [])
    )
    
    for genre_id, genre_name in genres_dict.items():
        column = (f'is_{genre_name.lower().replace("&", "e").replace(" ", "_")}')
        df[column] = true_genres_id.apply(lambda x: 1 if genre_id in x else 0)

    return df


def dummy_origin_country(df, country_set):
    true_origin_country = df['origin_country'].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else (x if isinstance(x, list) else [])
    )
    for country_name in country_set:
        column = (f"is_{country_name.lower()}")
        df[column] = true_origin_country.apply(lambda x: 1 if x and country_name in x else 0)
    return df


def dummy_media_type(data):
    if data == "tv":
        return 1
    return 0
