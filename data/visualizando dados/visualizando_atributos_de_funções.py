import pandas as pd

df = pd.read_csv("final_df.csv")
print(df.head())


# Alguns desses atributos são extremamente interessantes e não me arrependo de coletar eles
# Mas não são necessários para o ml, vamos evitar a multicolinearidade e excluir elas

# Simplesmente dropar essas colunas
df = df.drop(columns=['is_dorama', 'is_cartoon', 'is_anime'])

# Dropar as colunas de sazonalidade tb
df = df.drop(columns=['watched_time_dawn','watched_time_morning','watched_time_afternoon','watched_time_night'])


# Dropar mais colunas de sazonalidade
df = df.drop(columns=['seg_views', 'ter_views', 'qua_views', 'qui_views', 'sex_views', 'sab_views', 'dom_views', 'jan_views'
                       ,'fev_views','mar_views','abr_views','mai_views','jun_views','jul_views','ago_views','set_views','out_views'
                       ,'nov_views', 'dez_views'])