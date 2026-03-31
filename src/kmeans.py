

COLUMNS_SELECTION = ['Profile Name',
'WatchedTime',
'age_of_title',
'vote_average',
'popularity',
"is_natalino",
"is_super_heroi",
"is_dorama",
"is_kids",
"is_dystopian",
"is_based_on_book",
"is_anime",
"is_action",
"is_adventure",
"is_animation",
"is_comedy",
"is_crime",
"is_documentary",
"is_drama",
"is_family",
"is_fantasy",
"is_history",
"is_horror",
"is_music",
"is_mystery",
"is_romance",
"is_science_fiction",
"is_tv_movie",
"is_thriller",
"is_war",
"is_western",
"is_action_e_adventure",
"is_news",
"is_reality",
"is_sci-fi_e_fantasy",
"is_soap",
"is_talk",
"is_war_e_politics",
"is_it",
"is_kr",
"is_lu",
"is_es",
"is_mw",
"is_br",
"is_ch",
"is_no",
"is_de",
"is_ie",
"is_se",
"is_th",
"is_tr",
"is_co",
"is_fr",
"is_in",
"is_nl",
"is_is",
"is_us",
"is_dk",
"is_au",
"is_ar",
"is_ca",
"is_jp",
"is_gb",
"is_fi",
"is_cn",
"is_pl",
"is_mx",
"is_ph",
"is_hk",
"1970s",
"1980s",
"adventure",
"alien",
"amused",
"animals",
"anime",
"anthology",
"based_on_comic",
"based_on_manga",
"based_on_novel_or_book",
"based_on_true_story",
"biography",
"cartoon",
"christmas",
"coming_of_age",
"competition",
"corruption",
"dark_comedy",
"death",
"demon",
"detective",
"dog",
"dramatic",
"drugs",
"dystopia",
"family",
"family_relationships",
"fbi",
"female_protagonist",
"friends",
"friendship",
"gay_theme",
"ghost",
"high_school",
"holiday",
"horror",
"husband_wife_relationship",
"infidelity",
"investigation",
"kidnapping",
"lgbt",
"london__england",
"los_angeles__california",
"love",
"love_triangle",
"magic",
"marriage",
"martial_arts",
"mecha",
"miniseries",
"monster",
"murder",
"musical",
"new_york_city",
"parent_child_relationship",
"police",
"politics",
"prison",
"revenge",
"road_trip",
"romance",
"romantic",
"romcom",
"school",
"sequel",
"serial_killer",
"short_film",
"shounen",
"sibling_relationship",
"sitcom",
"slice_of_life",
"small_town",
"sports",
"stand-up_comedy",
"super_power",
"superhero",
"supernatural",
"survival",
"suspenseful",
"teenager",
"time_travel",
"true_crime",
"villain",
"woman_director",
"world_war_ii"]


CLUSTER_FEATURES = [
    "Profile Name",
    "WatchedTime",
    "age_of_title",
    "vote_average",
    "popularity",
    #"is_natalino",
    "is_super_heroi",
    "is_dorama",
    #"is_dystopian",
    "is_anime",
    "is_action",
    "is_adventure",
    "is_animation",
    "is_comedy",
    "is_crime",
    "is_documentary",
    "is_drama",
    "is_family",
    "is_fantasy",
    "is_history",
    "is_horror",
    "is_mystery",
    "is_romance",
    "is_thriller",
    "is_war",
    #"is_other_country",
    "is_kr",
    "is_br",
    #"is_fr",
    "is_us",
    "is_jp"
]

def nomear_cluster(cluster_profiles):

    global_mean = cluster_profiles.mean()
    global_std = cluster_profiles.std()

    cluster_names = {}

    for cluster_id, row in cluster_profiles.iterrows():

        score = (row - global_mean) / (global_std + 1e-6)
        strong = score.sort_values(ascending=False).head(5)
        s = strong.to_dict()

        if row["is_anime"] > 0.45 or row["is_jp"] > 0.6:
            name = "Otaku"

        elif row["is_dorama"] > 0.45 or row["is_kr"] > 0.6:
            name = "Dorameiro"

        elif row["is_super_heroi"] > 0.45:
            name = "Super-Herói"

        elif row["is_horror"] > 0.3 or row["is_thriller"] > 0.4:
            name = "Mistério"

        elif row["is_animation"] > 0.4 or row["is_family"] > 0.4:
            name = "Kids"

        elif row["vote_average"] > 7.5:
            name = "Cult"

        elif row["age_of_title"] > 10:
            name = "Ampulheta"

        else:
            name = "Eclético"

        cluster_names[cluster_id] = name

        # debug
        print(f"\nCluster {cluster_id} → {name}")
        print("Top desvios:")
        print(strong)
    return cluster_names

def check_perfil_vazio(profile_row):
    if profile_row["WatchedTime"] < 50:
        return "Vazio"
    
    return profile_row["cluster_name"]
