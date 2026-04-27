# service_modeling.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble       import RandomForestClassifier
from sklearn.metrics        import classification_report
from sklearn.utils.class_weight import compute_class_weight
from sklearn.utils import resample

# Paths & constants
SVC_CSV      = "results/processed/trace_services_expanded.csv"
NROWS_SAMPLE = 20000  # adjust up if you want more data

def main():
    # 1) Load sample, drop NaNs, cast labels
    svc = pd.read_csv(SVC_CSV, nrows=NROWS_SAMPLE)
    svc = svc.dropna(subset=["AssignedTo"])
    svc["AssignedTo"] = svc["AssignedTo"].astype(int)
    
    print("\n=== AssignedTo counts (before) ===")
    print(svc["AssignedTo"].value_counts(), "\n")
    
    # 2) Drop classes with <2 samples (for stratify)
    counts = svc["AssignedTo"].value_counts()
    valid  = counts[counts >= 2].index.tolist()
    if len(valid) != len(counts):
        drop = set(counts.index) - set(valid)
        print("Dropping classes with <2 examples:", drop, "\n")
        svc = svc[svc["AssignedTo"].isin(valid)]
    
    print("=== AssignedTo counts (after) ===")
    print(svc["AssignedTo"].value_counts(), "\n")
    
    # 3) Split features & labels
    sem_cols = [c for c in svc.columns if c.startswith("sem_")]
    features = sem_cols + ["CPUDemand"]
    
    X = svc[features]
    y = svc["AssignedTo"]
    print(f"Loaded {X.shape[0]} samples, {len(features)} features.\n")
    
    # 4) Train/test split
    Xtr, Xte, ytr, yte = train_test_split(
        X, y, stratify=y, test_size=0.2, random_state=0
    )
    print(f"Train: {Xtr.shape[0]} samples, Test: {Xte.shape[0]} samples\n")
    
    # 5A) Baseline: RF with class‐weight balancing
    weights = compute_class_weight("balanced", classes=ytr.unique(), y=ytr)
    cw = dict(zip(ytr.unique(), weights))
    print("Class weights:", cw, "\n")
    
    clf_wt = RandomForestClassifier(
        n_estimators = 100,
        max_depth    = 15,
        class_weight = cw,
        random_state = 0
    )
    clf_wt.fit(Xtr, ytr)
    print("=== RF with class weights ===")
    print(classification_report(yte, clf_wt.predict(Xte)))
    
    # 5B) Manual oversampling of train set to balance classes
    df_train = pd.concat([Xtr, ytr.rename("AssignedTo")], axis=1)
    max_size = df_train["AssignedTo"].value_counts().max()
    
    oversampled = []
    for cls, group in df_train.groupby("AssignedTo"):
        oversampled.append(
            resample(group,
                     replace=True,
                     n_samples=max_size,
                     random_state=0)
        )
    df_res = pd.concat(oversampled)
    X_res = df_res[features]
    y_res = df_res["AssignedTo"]
    print("\nAfter oversampling, class counts:", y_res.value_counts().to_dict(), "\n")
    
    clf_os = RandomForestClassifier(
        n_estimators = 100,
        max_depth    = 15,
        random_state = 0
    )
    clf_os.fit(X_res, y_res)
    print("=== RF after manual oversampling ===")
    print(classification_report(yte, clf_os.predict(Xte)))


if __name__ == "__main__":
    main()
