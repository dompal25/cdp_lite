import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve

def classification_report_df(y_true, y_prob, threshold=0.5):
    y_pred = (y_prob >= threshold).astype(int)
    tp = ((y_true==1)&(y_pred==1)).sum()
    fp = ((y_true==0)&(y_pred==1)).sum()
    tn = ((y_true==0)&(y_pred==0)).sum()
    fn = ((y_true==1)&(y_pred==0)).sum()
    precision = tp / max(tp+fp, 1)
    recall = tp / max(tp+fn, 1)
    auc = roc_auc_score(y_true, y_prob)
    ap = average_precision_score(y_true, y_prob)
    return pd.DataFrame([{
        "threshold": threshold, "precision": precision, "recall": recall,
        "roc_auc": auc, "avg_precision": ap, "tp": tp, "fp": fp, "tn": tn, "fn": fn
    }])

def uplift_by_decile(y_true, y_prob, k=10):
    df = pd.DataFrame({"y":y_true, "p":y_prob}).sort_values("p", ascending=False).reset_index(drop=True)
    n = len(df)
    rows = []
    for i in range(k):
        lo = int(i*n/k); hi = int((i+1)*n/k)
        part = df.iloc[lo:hi]
        rows.append({"decile": i+1, "n": len(part), "rate": part["y"].mean()})
    return pd.DataFrame(rows)
