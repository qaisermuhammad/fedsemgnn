# semantic_server5_model.py

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# --- Step 1: Load a larger chunk ---
SVC_CSV = "results/processed/trace_services_expanded.csv"
NROWS   = 50000  # increase if memory allows

print(f"\nLoading first {NROWS} rows from {SVC_CSV}...")
svc_df = pd.read_csv(SVC_CSV, nrows=NROWS)
svc_df = svc_df.dropna(subset=["AssignedTo"])
svc_df["AssignedTo"] = svc_df["AssignedTo"].astype(int)

print("AssignedTo counts:")
print(svc_df["AssignedTo"].value_counts(), "\n")

# --- Step 2: Visualize semantic clusters ---
sem_cols = [c for c in svc_df.columns if c.startswith("sem_")]
print("Running t-SNE on semantic vectors...")
Z = TSNE(n_components=2, random_state=0).fit_transform(svc_df[sem_cols])

plt.figure(figsize=(8,6))
plt.scatter(Z[:,0], Z[:,1], c=svc_df["AssignedTo"], cmap="tab10", s=5)
plt.title("t-SNE of Semantic Vectors by AssignedTo")
plt.xlabel("Dim 1"); plt.ylabel("Dim 2")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("results/processed/tsne_semantic_clusters.png", dpi=500)
plt.close()
print("✅ Saved t-SNE plot to results/processed/tsne_semantic_clusters.png")

# --- Step 3: Add time-aware and demand features ---
features = sem_cols + ["CPUDemand", "Step"]

# --- Step 4: Create binary target for Server 5 ---
svc_df["Label"] = (svc_df["AssignedTo"] == 5).astype(int)
print(f"\nBinary class counts for Server 5:\n{svc_df['Label'].value_counts()}\n")

# --- Step 5: Train binary classifier ---
X = svc_df[features]
y = svc_df["Label"]

Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=0)
clf.fit(Xtr, ytr)

ypred = clf.predict(Xte)
print("=== Binary Classification Report (Server 5 detection) ===")
print(classification_report(yte, ypred))
