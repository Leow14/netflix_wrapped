import pandas as pd
import time
from src.tmdb_search import get_tmdb_id, tmdb_search

initial_time = time.time()

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

keggle_base = pd.read_csv('data/archive/netflix_titles.csv')
print(keggle_base.columns)

c = 1
for title in keggle_base['title']:
    title, tmdb_id, media_type = get_tmdb_id(title)
    print(f'{c}/{len(keggle_base["title"])} | {title}')
    nova_linha = tmdb_search(title, tmdb_id, media_type)
    tmdb_base = pd.concat([tmdb_base, pd.DataFrame([nova_linha])], ignore_index=True)
    c += 1

ending_time = time.time()

print(f'Script finalizado. Run time = {ending_time - initial_time}')

tmdb_base.to_csv('data/processed/keggle_tmdb.csv', index=False, encoding="utf-8-sig")


