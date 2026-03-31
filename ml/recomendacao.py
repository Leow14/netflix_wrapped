import sys
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.features import selecionando_features_finais, FEATURES_CONTEUDO
from src.constants import PROFILES_NAMES_DF 
import pandas as pd
from src.random_forest import load_data

lista_de_dfs = []
users = PROFILES_NAMES_DF["Profile Name"].tolist()
final_base_global = None

for user in users:
    original_user = user
    user = user.lower().strip().replace(" ", "_")
    _, target_col, keggle, df = load_data(user, "engagement_score")

    if user not in df.columns:
        print(f"Usuário {user} não encontrado, pulando...")
        continue

    # Começando o treinamento do ML
    df_treino = df[df[user] == 1].copy()

    # Dropando colunas não utéis ao df e separando treino x e target
    X = selecionando_features_finais(df_treino).drop(columns=["title", "Profile Name"], errors="ignore")
    y = df_treino[target_col]

    # Dividindo teste e treino. Treino 80%, teste 20%
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Iniciando floresta aleatória com 100 árvores.
    model = RandomForestRegressor(n_estimators=100, random_state=42)

    # Treinando o modelo de fato
    model.fit(X_train, y_train)

    # Gerando a previsão do modelo
    prediction = model.predict(X_test)

    # Calcula a acurácia do modelo.
    mse = mean_squared_error(y_test, prediction)
    rmse = np.sqrt(mse)

    r2 = r2_score(y_test, prediction)
    mae = mean_absolute_error(y_test, prediction)

    print(f"Acurácia do modelo:")
    print(f"R2 Score = {r2}")
    print(f"Mean Absolute Error = {mae}")
    print(f"Root Mean Square Error = {rmse}")

    # Calculando a importância de cada coluna
    
    #importances = pd.Series(model.feature_importances_, index=X.columns)
    #importances.nlargest(30).plot(kind='barh')
    #plt.title(f"O que mais define o gosto de {user}?")
    #plt.show()

    # Base com os títulos que o usuário n viu ainda
    df_unseen = df[df[user] == 0].copy()

    colunas_desejadas = FEATURES_CONTEUDO

    final_base = pd.concat([df_unseen, keggle], ignore_index=True)
    final_base = final_base[colunas_desejadas]
    final_base = final_base.drop_duplicates(subset=['title'], keep='first').reset_index(drop=True)

    X_unseen = final_base[X.columns].apply(pd.to_numeric, errors='coerce').fillna(0)
    final_base["predicted_engagement"] = model.predict(X_unseen)
    final_base["profile_name"] = original_user

    lista_de_dfs.append(final_base)

    n = 20
    top = final_base.sort_values("predicted_engagement", ascending=False).head(n)
    print(f"\nTOP {n} RECOMENDAÇÕES DE {user}:")  
    print(top[['title', "predicted_engagement"]])

final_base_global = pd.concat(lista_de_dfs, ignore_index=True)
print(final_base_global.shape)
print(final_base_global.columns)
final_base_global.to_csv(f"data/processed/random_forest_regressor.csv", index=False, encoding="utf-8-sig")