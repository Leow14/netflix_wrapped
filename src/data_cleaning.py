import pandas as pd
import unicodedata
import re
import ast
from src.constants import DONTS

# Arquivo de limpeza e tratamento de títulos.
# Listas de palavras-chave para a verificação dos títulos;

check_natalino_list = ["christmas", "xmas", "santa claus", "christmas movie", "holiday"]

check_super_list = ["superhero", "super hero", "super-hero", "superpower", "super power", "super-power", 
                    "marvel", "dc comics", "based on comic", "comic book"]

check_kids_list = ["children", "kids", "preschool", "talking animal", "talking train",
            "fairy tale", "puppet", "animated series", "flying horse", "pony", "unicorn"]

check_dystopian_list = [
    "dystopia", "dystopian future", "post-apocalyptic", "post apocalyptic", "totalitarianism", "surveillance"]

check_based_on_book_list = [
    "based on novel", "based on book", "based on young adult novel",
    "based on comic", "based on graphic novel", "based on manga"]

check_anime_kw_list = [
    "anime", "manga", "based on manga"]

# Tabela de codificação da classificação indicativa:
CONTENT_RATING_MAP = {
    # EUA - Filmes
    "G": 0, "PG": 1, "PG-13": 2, "R": 5, "NC-17": 5,
    # EUA - Séries
    "TV-G": 0, "TV-Y": 0, "TV-Y7": 1, "TV-PG": 1,
    "TV-14": 3, "TV-MA": 5,
}

KEY_WORDS_MAP = {
    'based on novel or book'    : 1,
    'anime'                     : 2,
    'woman director'            : 3,
    'romance'                   : 4,
    'love'                      : 4,
    'friendship'                : 5,
    'murder'                    : 6,
    'based on true story'       : 7,
    'biography'                 : 8,
    'high school'               : 9,
    'lgbt'                      : 10,
    'gay theme'                 : 10,
    'revenge'                   : 11,
    'based on manga'            : 12,
    'new york city'             : 13,
    'sports'                    : 14,
    'miniseries'                : 15,
    'supernatural'              : 16,
    'martial arts'              : 17,
    'coming of age'             : 18,
    'magic'                     : 20,
    'family'                    : 21,
    'family relationships'      : 21,
    'parent child relationship' : 21,
    'sibling relationship'      : 21, 
    'husband wife relationship' : 21,
    'christmas'                 : 22,
    'stand-up comedy'           : 23,
    'sequel'                    : 24,
    'based on comic'            : 25,
    'superhero'                 : 26,
    'super power'               : 26,
    'school'                    : 27,
    'female protagonist'        : 28,
    'sitcom'                    : 29,
    'drugs'                     : 30,
    'shounen'                   : 31,
    'survival'                  : 32,
    'serial killer'             : 33,
    'california'                : 34,
    'los angeles'               : 34,
    'police'                    : 35,
    'remake'                    : 36,
    'dark comedy'               : 37,
    'investigation'             : 38,
    'detective'                 : 38,
    'small town'                : 39,
    'world war ii'              : 40,
    'amused'                    : 41,
    'dystopia'                  : 42,
    'short film'                : 43,
    'alien'                     : 44,
    'musical'                   : 45,
    'politics'                  : 46,
    'death'                     : 47,
    'england'                   : 48,
    'london'                    : 48,
    'romcom'                    : 49,
    'dramatic'                  : 50,
    'competition'               : 51,
    'adventure'                 : 52,
    'love triangle'             : 53,
    'monster'                   : 54,
    'ghost'                     : 55,
    'true crime'                : 56,
    'villain'                   : 57,
    'slice of life'             : 58,
    'demon'                     : 59,
    'prison'                    : 60,
}

DIRECTORS_MAP = {
    "Jay Karas"                 : 1,
    "Martin Scorsese"           : 2,
    "Steven Spielberg"          : 3,
    "Cathy Garcia-Sampana"      : 4,
    "Robert Rodriguez"          : 5,
    "Don Michael Paul"          : 6,
    "Justin G. Dyck"            : 7,
    "Quentin Tarantino"         : 8,
    "Clint Eastwood"            : 9,
    "Robert Vince"              : 10,
    "Steven Brill"              : 11,
    "Steven Soderbergh"         : 12,
    "Toshiya Shinohara"         : 13,
    "Ron Howard"                : 14,
    "Lasse Hallström"           : 15,
    "Joe Berlinger"             : 16,
    "Rob Minkoff"               : 17,
    "Guillermo del Toro"        : 18,
}

REVERSE_KEYWORD_MAP = {}
for key, value in KEY_WORDS_MAP.items():
    if value not in REVERSE_KEYWORD_MAP:
        REVERSE_KEYWORD_MAP[value] = key

KEY_WORDS_LIST = ['1970s', '1980s', 'adventure', 'alien', 'amused',
       'animals', 'anime', 'anthology', 'based on comic', 'based on manga',
       'based on novel or book', 'based on true story', 'biography', 'cartoon',
       'christmas', 'coming of age', 'competition', 'corruption',
       'dark comedy', 'death', 'demon', 'detective', 'dog', 'dramatic',
       'drugs', 'dystopia', 'family', 'family relationships', 'fbi', 
       'female protagonist', 'friends', 'friendship', 'gay theme', 
       'ghost', 'high school', 'holiday', 'horror',
       'husband wife relationship', 'infidelity', 'investigation',
       'kidnapping', 'lgbt', 'london, england', 'los angeles, california',
       'love', 'love triangle', 'magic', 'marriage', 'martial arts', 'mecha',
       'miniseries', 'monster', 'murder', 'musical', 'new york city',
       'parent child relationship', 'police', 'politics', 'prison',
       'revenge', 'road trip', 'romance', 'romantic', 'romcom', 'school',
       'sequel', 'serial killer', 'short film', 'shounen',
       'sibling relationship', 'sitcom', 'slice of life', 'small town',
       'sports', 'stand-up comedy', 'super power', 'superhero', 'supernatural',
       'survival', 'suspenseful', 'teenager', 'time travel', 'true crime',
       'villain', 'woman director', 'world war ii']


KEY_WORDS_LIST = [ keyword.strip().lower().replace(',', '_').replace(' ', '_') for keyword in KEY_WORDS_LIST] 
KEY_WORDS_SET = set(KEY_WORDS_LIST)

def creating_keywords_columns(df):
    for keyword in KEY_WORDS_LIST:
        if keyword not in df.columns:
            df[keyword] = 0
    return df

def converting_keywords_columns(df):
    df = creating_keywords_columns(df)

    for index, row in df.iterrows():
        keywords = row["keywords"]

        if not keywords:
            continue

        if isinstance(keywords, str):
            try:
                keywords = ast.literal_eval(keywords)
            except:
                continue
        
        if not isinstance(keywords, list):
            continue

        for keyword in keywords:
            keyword = keyword.strip().lower().replace(',', '_').replace(' ', '_')
            if keyword in KEY_WORDS_SET:
                df.at[index, keyword] = 1

    return df



def limpar_titulo(titulo: str, donts=DONTS) -> str:
    titulo = titulo.lower()
    if '_' in titulo:
        titulo = titulo[:titulo.find('_')]
    if (':') in titulo:
        titulo = titulo[:titulo.find(':')]

    for i in range(10):
        removed = False
        for text in donts:
            if titulo.startswith(text):
                titulo = titulo[titulo.find(':')+1:]
                removed = True
                break
            elif text in titulo:
                titulo = titulo.replace(text, '')
                titulo = titulo.strip()
                removed = True
                break
        if removed == False:
            return titulo

    titulo = titulo.strip()
    return titulo

def convert_text_csv(text):
    if pd.isna(text):
        return text
    
    text = str(text).lower().strip()
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return text


def converting_timedelta(val):
    if pd.isnull(val):
        return pd.NaT
    if isinstance(val, pd.Timedelta):
        return val
    if isinstance(val, pd.Timestamp):
        return pd.NaT
    
    try:
        return pd.to_timedelta(val)
    except:
        return pd.NaT

# Verificação geral (para cada tipo de check)
def _check_keywords(source, keyword_list):
    if isinstance(source, list):
        source_lower = [k.lower() for k in source]
        return 1 if any(k in source_lower for k in keyword_list) else 0
    if isinstance(source, str):
        source_lower = source.lower()
        return 1 if any(k in source_lower for k in keyword_list) else 0
    return 0

def check_natalino(source):
    return _check_keywords(source, check_natalino_list)

def check_super(source):
    return _check_keywords(source, check_super_list)

def check_kids(source):
    return _check_keywords(source, check_kids_list)

def check_dystopian(source):
    return _check_keywords(source, check_dystopian_list)

def check_based_on_book(source):
    return _check_keywords(source, check_based_on_book_list)

def check_anime_kw(source):
    return _check_keywords(source, check_anime_kw_list)

def convert_content_rating(rating):
    if not rating:
        return -1
    return CONTENT_RATING_MAP.get(str(rating).strip(), -1)

def convert_director(director):
    if not director:
        return -1
    return DIRECTORS_MAP.get(str(director).strip(), -1)

def convert_keywords(keywords):
    if not isinstance(keywords, str):
        return -1

# Checando se o título está na lista.
def check_list(title, list):
    if title in list:
        return 1
    return 0

# Checando a "row" (ou seja, linha) e fazendo verificações com isso.
def check_anime(row):
    is_japanese     = row["is_jp"]
    is_korean       = row["is_kr"]
    is_chinese      = row["is_cn"]
    is_animation    = row["is_animation"]
    if is_animation and (is_japanese or is_korean or is_chinese):
        return 1
    return 0

def check_dorama(media_type, production_countries, keywords):
    is_dorama = 0
    if media_type == "tv" and production_countries:
        is_kr = "KR" in production_countries
        kw_dorama = any(k in keywords for k in ["korean drama", "k-drama", "south korean"])
        if is_kr or kw_dorama:
            is_dorama = 1
    return is_dorama


def is_latin(text):
    if not isinstance(text, str):
        return False
    cleaned = re.sub(r'[\s\d\W]', '', text)
    return bool(cleaned) and all(ord(c) < 591 for c in cleaned)
  
def new_check_kids(keywords, content_rating):  
    kw_match = any(k in check_kids_list for k in keywords) if keywords else False

    rating_match = int(content_rating) <= 1 if isinstance(content_rating, str) else False
    return int(kw_match or rating_match)