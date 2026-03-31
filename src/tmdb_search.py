import requests
import os
from dotenv import load_dotenv
from src.data_cleaning import (
    check_natalino, check_super, check_kids,
    check_dystopian, check_based_on_book, check_anime_kw,
    convert_content_rating, check_dorama
)
import pandas as pd
from src.constants import TMDB_KEY, TMDB_URL
import time

load_dotenv()

TMDB_KEY=os.getenv("TMDB_KEY")
TMDB_URL="https://api.themoviedb.org/3"

def get_tmdb_id(title, language='pt-BR'):
    tmdb_id, media_type = 0, ''
    params = {
        "api_key": TMDB_KEY,
        "query": title,
        "language" : language,
        "include_adult": False
    }
    url = f"{TMDB_URL}/search/multi"
    try:
        response = requests.get(url=url, params=params, timeout=15)
        data = response.json()

        if data and data.get("results"):
            result = [r for r in data["results"] if r.get("media_type") in ["tv", "movie"]]
            if not result:
                print(f"Título {title} não encontrado.")
            
            result_filtered = [r for r in result if r.get("vote_count", 0) > 3]

            if result_filtered:
                result = result_filtered

            result = result[0]
            
            media_type = result.get("media_type")
            tmdb_id = result.get("id")

            return title, tmdb_id, media_type
        else:
            print(f"Título {title} não encontrado.")
    except Exception as error:
        print(f"Erro ao buscar. Erro = {error}")
        return title, 0, ''
    return title, tmdb_id, media_type


def get_keywords(tmdb_id, media_type):
    try:
        url = f"{TMDB_URL}/{media_type}/{tmdb_id}/keywords"
        response = requests.get(url=url, params={"api_key": TMDB_KEY}, timeout=15)
        data = response.json()
        kw_list = data.get("keywords") or data.get("results") or []
        return [kw["name"].lower() for kw in kw_list]
    except:
        return []


def get_director(tmdb_id, media_type):
    try:
        if media_type == "movie":
            url = f"{TMDB_URL}/movie/{tmdb_id}/credits"
            response = requests.get(url=url, params={"api_key": TMDB_KEY}, timeout=15)
            crew = response.json().get("crew", [])
            directors = [p["name"] for p in crew if p.get("job").lower() == "director"]
            return directors[0] if directors else None
        else:
            url = f"{TMDB_URL}/tv/{tmdb_id}"
            response = requests.get(url=url, params={"api_key": TMDB_KEY}, timeout=15)
            creators = response.json().get("created_by", [])
            return creators[0]["name"] if creators else None
    except:
        return None


def get_content_rating(tmdb_id, media_type):

    try:
        if media_type == "movie":
            url = f"{TMDB_URL}/movie/{tmdb_id}/release_dates"
            response = requests.get(url=url, params={"api_key": TMDB_KEY}, timeout=15)
            results = response.json().get("results", [])
            for entry in results:
                if entry.get("iso_3166_1") == "US":
                    releases = entry.get("release_dates", [])
                    for r in releases:
                        cert = r.get("certification", "")
                        if cert:
                            return cert

        else:
            url = f"{TMDB_URL}/tv/{tmdb_id}/content_ratings"
            response = requests.get(url=url, params={"api_key": TMDB_KEY}, timeout=15)
            results = response.json().get("results", [])
            for entry in results:
                if entry.get("iso_3166_1") == "US":
                    return entry.get("rating", None)
    except:
        return None
    return None


def tmdb_search(title, tmdb_id, media_type, language="pt-BR"):
    details_url          = f"{TMDB_URL}/{media_type}/{tmdb_id}"
    details_params       = {"api_key": TMDB_KEY, "language" : language}
    details_data         = {}
    overview             = ""
    duration             = None
    production_countries = None
    num_seasons          = None
    
    try:
        details_response = requests.get(url=details_url, params=details_params, timeout=15)
        details_data     = details_response.json()
        overview         = details_data.get("overview") or ""
        if media_type   == "movie":
            duration = details_data.get("runtime") or None
            p_c = details_data.get("production_countries")
            production_countries = []
            if p_c:
                for list in p_c:
                    production_countries.append(list["iso_3166_1"])
            else:
                production_countries = None
        else:
            duration = details_data.get("episode_run_time") or None
            production_countries = details_data.get("origin_country") or None
            num_seasons = details_data.get("number_of_seasons") or None
    except:
        overview = ""
        duration = None
        production_countries = None
        num_seasons = None
        

    poster_path = details_data.get("poster_path")
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
    
    # Séries contém nome e filmes contém título, por isso é necessário unifica-los 
    title_unified = details_data.get("title") or details_data.get("name")
    date_unified = details_data.get("release_date") or details_data.get("first_air_date")
    
    # Pegando os genres
    genres = details_data.get("genres", [])
    genres_id = [genre["id"] for genre in genres]

    # Buscas adicionais (só executam se o tmdb_id for válido)
    keywords       = get_keywords(tmdb_id, media_type)       if tmdb_id else []
    director       = get_director(tmdb_id, media_type)       if tmdb_id else None
    raw_rating     = get_content_rating(tmdb_id, media_type) if tmdb_id else None
    
    age_of_title = None
    if date_unified:
        try:
            release_year = int(str(date_unified)[:4])
            age_of_title = pd.Timestamp.now().year - release_year
        except:
            age_of_title = None

    return {
        "netflix_title"   : title,
        "title"           : title_unified,
        "genre_ids"       : genres_id,
        "poster_path"     : poster_url,
        "media_type"      : media_type,
        "popularity"      : details_data.get("popularity"),
        "age_of_title"    : age_of_title,
        "vote_average"    : details_data.get("vote_average"),
        "vote_count"      : details_data.get("vote_count"),
        "run_time"        : duration,
        "num_seasons"     : num_seasons,
        "origin_country"  : production_countries,
        "keywords"        : keywords,
        "director"        : director,
        "content_rating"  : convert_content_rating(raw_rating),
        "is_natalino"     : check_natalino(keywords) or check_natalino(overview),
        "is_super_heroi"  : check_super(keywords)    or check_super(overview),
        "is_dorama"       : check_dorama(media_type, production_countries, keywords),
        "is_kids"         : check_kids(keywords),
        "is_dystopian"    : check_dystopian(keywords),
        "is_based_on_book": check_based_on_book(keywords),
        "is_anime"        : check_anime_kw(keywords),
    }
