# ── FEATURE ENGINEERING FOR LIGHTGBM ─────────────────────────────

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import f1_score
import scipy.sparse as sp

RUN_NAME_LGBM = "lgbm_tuned_v2"   # ← all outputs saved with this prefix


# ── STEP 1: BUILD TEXT COLUMN ─────────────────────────────────────
# Fields used:
#   summary                        → primary free text (main signal)
#   tier2_consolidated_description → detailed complaint context
#   Service                        → product/service type
#   tier1                          → broad complaint category
# EXCLUDED: keyword_group (leaks label info directly)

def build_lgbm_text(df):
    return (
        df['Service'].fillna('') + ' | ' +
        df['tier1'].fillna('') + ' | ' +
        df['tier2_consolidated_description'].fillna('') + ' | ' +
        df['summary'].fillna('')
    )

train_text = build_lgbm_text(df_tr)
val_text   = build_lgbm_text(df_val)
test_text  = build_lgbm_text(df_te)

print(f"Sample text row:\n{train_text.iloc[0][:300]}...\n")


# ── STEP 2: WORD N-GRAMS (1,2,3) ─────────────────────────────────
tfidf_word = TfidfVectorizer(
    max_features=30000,
    ngram_range=(1, 3),
    sublinear_tf=True,
    min_df=2,
    analyzer='word'
)
X_tr_word  = tfidf_word.fit_transform(train_text)
X_val_word = tfidf_word.transform(val_text)
X_te_word  = tfidf_word.transform(test_text)

print(f"Word TF-IDF:  {X_tr_word.shape[1]:,} features")


# ── STEP 3: CHARACTER N-GRAMS (2,4) ──────────────────────────────
tfidf_char = TfidfVectorizer(
    max_features=15000,
    ngram_range=(2, 4),
    sublinear_tf=True,
    min_df=3,
    analyzer='char_wb'
)
X_tr_char  = tfidf_char.fit_transform(train_text)
X_val_char = tfidf_char.transform(val_text)
X_te_char  = tfidf_char.transform(test_text)

print(f"Char TF-IDF:  {X_tr_char.shape[1]:,} features")


# ── STEP 4: SERVICE AS ONE-HOT ────────────────────────────────────
ohe_svc = OneHotEncoder(handle_unknown='ignore', sparse_output=True)
X_tr_svc  = ohe_svc.fit_transform(df_tr[['Service']].fillna('Unknown'))
X_val_svc = ohe_svc.transform(df_val[['Service']].fillna('Unknown'))
X_te_svc  = ohe_svc.transform(df_te[['Service']].fillna('Unknown'))

print(f"Service OHE:  {X_tr_svc.shape[1]:,} features")


# ── STEP 5: TIER1 AS ONE-HOT ─────────────────────────────────────
ohe_t1 = OneHotEncoder(handle_unknown='ignore', sparse_output=True)
X_tr_t1  = ohe_t1.fit_transform(df_tr[['tier1']].fillna('Unknown'))
X_val_t1 = ohe_t1.transform(df_val[['tier1']].fillna('Unknown'))
X_te_t1  = ohe_t1.transform(df_te[['tier1']].fillna('Unknown'))

print(f"Tier1 OHE:    {X_tr_t1.shape[1]:,} features")


# ── STEP 6: STACK ALL FEATURES ────────────────────────────────────
X_tr_final  = sp.hstack([X_tr_word,  X_tr_char,  X_tr_svc,  X_tr_t1])
X_val_final = sp.hstack([X_val_word, X_val_char, X_val_svc, X_val_t1])
X_te_final  = sp.hstack([X_te_word,  X_te_char,  X_te_svc,  X_te_t1])

print(f"\nFinal feature matrix: {X_tr_final.shape}")
print(f"  Total features: {X_tr_final.shape[1]:,}")


# ── STEP 7: TRAIN LIGHTGBM ────────────────────────────────────────
from lightgbm import LGBMClassifier

lgbm_tuned = OneVsRestClassifier(
    LGBMClassifier(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        num_leaves=31,
        min_child_samples=5,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
        verbose=-1
    ),
    n_jobs=-1
)

lgbm_tuned.fit(X_tr_final, y_tr)
print("✓ LightGBM training complete")


# ── STEP 8: PER-TAG THRESHOLD TUNING ─────────────────────────────
lgbm_val_probs = lgbm_tuned.predict_proba(X_val_final)
tag_freq       = y_tr.sum(axis=0) / len(y_tr)
thresholds_lgbm = []

for i in range(NUM_LABELS):
    best_t, best_f = 0.5, 0.0
    for t in np.arange(0.10, 0.91, 0.05):
        f = f1_score(y_val[:, i], (lgbm_val_probs[:, i] > t).astype(int), zero_division=0)
        if f > best_f:
            best_f, best_t = f, t
    if tag_freq[i] > DOMINANT_FREQ:
        best_t = max(best_t, 0.65)
    if tag_freq[i] < RARE_FREQ:
        best_t = min(best_t, 0.35)
    thresholds_lgbm.append(best_t)

thresholds_lgbm = np.array(thresholds_lgbm)

macro_before = f1_score(y_val, (lgbm_val_probs > 0.5).astype(int),              average='macro', zero_division=0)
macro_after  = f1_score(y_val, (lgbm_val_probs > thresholds_lgbm).astype(int),  average='macro', zero_division=0)

print(f"\nVal Macro — global 0.5:    {macro_before:.4f}")
print(f"Val Macro — per-tag tuned: {macro_after:.4f}")
print(f"Lift from threshold tuning: +{macro_after - macro_before:.4f}")

np.save(f'saved_data/{RUN_NAME_LGBM}_tag_thresholds.npy', thresholds_lgbm)


# ── STEP 9: FINAL TEST EVALUATION ────────────────────────────────
from sklearn.metrics import classification_report

lgbm_test_probs = lgbm_tuned.predict_proba(X_te_final)
preds_lgbm      = (lgbm_test_probs > thresholds_lgbm).astype(int)

macro_test = f1_score(y_te, preds_lgbm, average='macro',   zero_division=0)
micro_test = f1_score(y_te, preds_lgbm, average='micro',   zero_division=0)
samp_test  = f1_score(y_te, preds_lgbm, average='samples', zero_division=0)

print("\n" + "=" * 55)
print(f"Run:        {RUN_NAME_LGBM}")
print(f"Macro F1:   {macro_test:.4f}   ← primary metric")
print(f"Micro F1:   {micro_test:.4f}")
print(f"Samples F1: {samp_test:.4f}")
print("=" * 55)
print(classification_report(y_te, preds_lgbm, target_names=valid_tags, zero_division=0))

# ── Save predictions ──
pred_df = df_te[['case_reference']].copy()
for i, tag in enumerate(valid_tags):
    pred_df[f'pred_{tag}'] = preds_lgbm[:, i]
    pred_df[f'prob_{tag}'] = lgbm_test_probs[:, i].round(3)

pred_df.to_csv(f'saved_data/{RUN_NAME_LGBM}_test_predictions.csv', index=False)
print(f"\nSaved: saved_data/{RUN_NAME_LGBM}_test_predictions.csv")
print(f"Saved: saved_data/{RUN_NAME_LGBM}_tag_thresholds.npy")
