import pandas as pd
import numpy as np
import matplotlib.pyplot as plt   

df = pd.read_csv("final_df.csv")

# Filtrando gêneros para a seleção de atributos

df = df[['is_br',
         'is_fr',
         'is_it',
         'is_cn',
         'is_hu',
         'is_kr',
         'is_pl',
         'is_in',
         'is_se',
         'is_mx',
         'is_za',
         'is_no',
         'is_fi',
         'is_th',
         'is_ca',
         'is_nl',
         'is_us',
         'is_tr',
         'is_lu',
         'is_is',
         'is_es',
         'is_jp',
         'is_de',
         'is_au',
         'is_dk',
         'is_ar',
         'is_gb',
         'is_co'
]]

df['is_european'] = df['is_es'] | df['is_de'] | df['is_fr'] | df['is_gb']
df['is_north_american'] = df['is_ca'] | df['is_us']
df = df.drop(columns=['is_es', 'is_de', 'is_fr', 'is_gb', 'is_us', 'is_ca', 'is_us'])

print(df.head())

df = df.sum()

# separa só as "is_country", depois eu faço
colunas_para_manter = df[df <= 5].index.tolist()  
print(colunas_para_manter)

# Criando um novo DataFrame apenas com as colunas filtradas  
df = df[colunas_para_manter]
print(df.head)

df = df.sort_values(ascending=False)

plt.figure(figsize=(10, 8))
plt.barh(df.index, df.values)
plt.xlabel("Somatória")
plt.ylabel("Gêneros")
plt.title("Distribuição de Gêneros no Dataset")

plt.tight_layout()

plt.show()



# DROP
# is_music, is_soap, is_family, is_western, is_reality
