import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from src.kmeans import COLUMNS_SELECTION, CLUSTER_FEATURES, nomear_cluster, check_perfil_vazio
from src.constants import PROFILES_NAMES_DF 
from src.features import fix_encoding
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.neighbors import KernelDensity
from sklearn.decomposition import PCA


# ?Carregando Dados
df = pd.read_csv("data/processed/final_df.csv")
perfis_kmeans = pd.read_csv("data/processed/perfis_kmeans.csv")
print(perfis_kmeans.index.tolist())
df["Profile Name"] = df["Profile Name"].apply(fix_encoding)
perfis_kmeans["Profile Name"] = perfis_kmeans["Profile Name"].apply(fix_encoding)

combined_profiles = pd.concat(
    [df.reset_index(), perfis_kmeans],
    ignore_index=True
)
combined_profiles = combined_profiles[CLUSTER_FEATURES]


# ? Conversão de dado
combined_profiles["WatchedTime"] = pd.to_timedelta(combined_profiles["WatchedTime"], errors="coerce")
combined_profiles["WatchedTime"] = combined_profiles["WatchedTime"].dt.total_seconds() / 60


# ? Gerando perfil médio por usuário
user_profiles = combined_profiles.groupby("Profile Name").mean()
profile_names = user_profiles.index.tolist()

print(profile_names)

# ? Gerando perfis sintéticos
# Convertendo para um array (formato esperado pelo sklearn)
#X_real = user_profiles.values

#kde = KernelDensity(kernel="gaussian", bandwidth=0.3)
#kde.fit(X_real)

#synthetic = kde.sample(100)
#synthetic_profiles = pd.DataFrame(synthetic, columns=user_profiles.columns)
#synthetic_profiles["Profile Name"] = [f"synthetic_{i}" for i in range(len(synthetic_profiles))]


# ? Juntando o perfil real com os sintéticos
real_profiles = user_profiles.copy()
real_profiles["Profile Name"] = profile_names

#all_profiles = pd.concat([real_profiles, synthetic_profiles], ignore_index=True)
all_profiles = real_profiles.copy()

# ? Preparando dados para o ML
base_features = all_profiles.drop(columns=["Profile Name"])

scaler = StandardScaler()
X_scaled = scaler.fit_transform(base_features)

# ? Calculando a curva de cotovelo
inertia = []

for k in range(1,10):
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    model.fit(X_scaled)
    inertia.append(model.inertia_)

plt.figure(figsize=(8,5))
plt.plot(range(1,10), inertia, marker = "o")

plt.xlabel("Número de clusters")
plt.ylabel("Inertia")
plt.show()

# ? Rodando Kmeans Final

kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_scaled)
all_profiles["cluster"] = clusters

# ? PCA (visualização)

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

viz_df = all_profiles.copy()
viz_df["PC1"] = X_pca[:,0]
viz_df["PC2"] = X_pca[:,1]
viz_df["cluster"] = clusters

plt.figure(figsize=(10,7))
sns.scatterplot(data=viz_df,x="PC1",y="PC2",hue="cluster",alpha=0.4)


# ? Filtra apenas usuários reais
real_users = PROFILES_NAMES_DF["Profile Name"].tolist()
real_df = viz_df[viz_df["Profile Name"].isin(real_users)]

sns.scatterplot(data=real_df,x="PC1",y="PC2",color="black",s=200,marker="X")

for _, row in real_df.iterrows():

    plt.text(row["PC1"],row["PC2"],row["Profile Name"],fontsize=10,weight="bold")

plt.title("Clusters de Perfis de Usuário")
plt.xlabel("PCA 1")
plt.ylabel("PCA 2")

plt.show()

# ? Perfil médio do cluster
cluster_profiles = base_features.copy()
cluster_profiles["cluster"] = clusters

cluster_profiles = cluster_profiles.groupby("cluster").mean()
print("\nPerfil médio dos clusters:\n")
print(cluster_profiles)


# ? Clusteres de cada usuário real
print(all_profiles[all_profiles["Profile Name"].isin(real_users)][["Profile Name","cluster"]])

cluster_map = nomear_cluster(cluster_profiles)
cluster_profiles["cluster_name"] = cluster_profiles.index.map(cluster_map)
all_profiles["cluster_name"] = all_profiles["cluster"].map(cluster_map)
all_profiles["final_profile"] = all_profiles.apply(check_perfil_vazio, axis=1)

# ? Mapenado por usuário
cluster_map = cluster_profiles["cluster_name"].to_dict()
all_profiles["cluster_name"] = all_profiles["cluster"].map(cluster_map)


# ? Resultado final
print("\nClusters nomeados:\n")
print(cluster_profiles[["cluster_name"]])

print("\nUsuários com seus perfis:\n")
print(
    all_profiles[
        all_profiles["Profile Name"].isin(real_users)
    ][["Profile Name", "cluster", "cluster_name", "final_profile"]]
)

print(
    all_profiles[
        all_profiles["Profile Name"] == "ANA PAULA AMORIM"
    ][["WatchedTime"]]
)

print(
    all_profiles[
        all_profiles["Profile Name"] == "Jose"
    ][["WatchedTime"]]
)

output_df = all_profiles.copy()

output_df = output_df.drop(columns=["PC1", "PC2"], errors="ignore")

output_df.to_csv("data/processed/kmeans.csv",index=False,encoding="utf-8-sig")