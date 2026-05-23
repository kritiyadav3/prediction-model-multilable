import re
import json
import pandas as pd
import numpy as np
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# =========================
# CONFIG — change paths/model here only
# =========================
TRAINED_3500_PATH   = "saved_data/final_training_dataset_llm_validated_noleak.csv"
NEW_7400_PATH       = "./builtin/new_7400_cases.csv"
TIER2_DESC_PATH     = "./builtin/Tier2_tier_description.csv"

OUT_APPENDED        = "saved_data/final_training_appended.csv"
OUT_SELECTION_AUDIT = "saved_data/new_case_selection_audit.csv"

# If you're on 768-dim swap to: "sentence-transformers/all-mpnet-base-v2"
EMBEDDING_MODEL  = "sentence-transformers/all-MiniLM-L6-v2"
SIM_THRESHOLD    = 0.35
TOP_N_PER_TAG    = 100
F1_THRESHOLD     = 0.75
MIN_SUPPORT      = 5

# =========================
# UNDERPERFORMING TAGS — from your results
# =========================
TAG_RESULTS = {
    "Fault":                                              {"f1": 0.1818, "support": 10},
    "Mishandled or inaccurate information - not personal":{"f1": 0.25,   "support": 6},
    "Non-financial loss":                                 {"f1": 0.3636, "support": 6},
    "Inadequate explanation of product":                  {"f1": 0.40,   "support": 7},
    "No notice of activity":                              {"f1": 0.0,    "support": 0},
    "Excess call/sms/mms charges":                        {"f1": 0.0,    "support": 0},
    "OOJ services":                                       {"f1": 0.0,    "support": 0},
    "General telecommunications enquiry":                 {"f1": 0.0,    "support": 0},
    "Defective notice":                                   {"f1": 0.0,    "support": 0},
    "Slow data speed":                                    {"f1": 0.6667, "support": 2},
    "Unsuitable":                                         {"f1": 0.6667, "support": 4},
    "Unwelcome/life threatening communications":          {"f1": 0.6667, "support": 6},
    "Not liable for contract":                            {"f1": 0.6667, "support": 4},
    "Customer Service Guarantee":                         {"f1": 0.6667, "support": 2},
    "Inadequate documentation":                           {"f1": 0.6667, "support": 4},
    "Restricted service":                                 {"f1": 0.7059, "support": 11},
    "Business loss":                                      {"f1": 0.7273, "support": 6},
    "Number problem":                                     {"f1": 0.7273, "support": 7},
    "Object to collection":                               {"f1": 0.75,   "support": 4},
    "Rudeness":                                           {"f1": 0.7692, "support": 7},
    "Missing payment":                                    {"f1": 0.80,   "support": 6},
    "Unfair contract terms":                              {"f1": 0.80,   "support": 6},
}

TARGET_TAGS = {
    tag for tag, v in TAG_RESULTS.items()
    if v["f1"] < F1_THRESHOLD or v["support"] < MIN_SUPPORT
}

print(f"Target underperforming tags ({len(TARGET_TAGS)}):")
for t in sorted(TARGET_TAGS):
    print(f"  [{TAG_RESULTS[t]['f1']:.2f} f1 | support={TAG_RESULTS[t]['support']}]  {t}")

# =========================
# LOAD
# =========================
df_3500    = pd.read_csv(TRAINED_3500_PATH)
df_7400    = pd.read_csv(NEW_7400_PATH)
tier2_desc = pd.read_csv(TIER2_DESC_PATH)

# Build tag → description map
cols_lower = {c.lower().strip(): c for c in tier2_desc.columns}
tag_col    = cols_lower.get("tier 2",              list(tier2_desc.columns)[0])
desc_col   = cols_lower.get("tier2_description",   list(tier2_desc.columns)[1])

tag_desc_map = {
    str(r[tag_col]).strip(): str(r[desc_col]).strip()
    for _, r in tier2_desc.iterrows()
    if str(r[tag_col]).strip()
}

# =========================
# HELPERS
# =========================
def parse_tags(s):
    """
    Handles both:
      - plain CSV:  "Fault, Rudeness, Slow data speed"
      - QC format:  "Fault (q=0.82, thr=0.5), Rudeness (q=0.71)"
    Returns a clean list of tag name strings.
    """
    if pd.isna(s) or str(s).strip() == "":
        return []
    s = str(s)
    # strip everything inside parentheses first
    s = re.sub(r"\(.*?\)", "", s)
    tags = [t.strip() for t in s.split(",") if t.strip()]
    return tags


def get_case_tags(row):
    """Try tier2_cleaned → tier2 → final_tags in order."""
    for col in ["tier2_cleaned", "tier2", "final_tags"]:
        val = row.get(col, "")
        if pd.notna(val) and str(val).strip() not in ("", "[]", "nan"):
            # final_tags may be a stringified Python list
            if col == "final_tags":
                try:
                    parsed = eval(str(val))
                    if isinstance(parsed, list):
                        return [str(t).strip() for t in parsed if str(t).strip()]
                except Exception:
                    pass
            tags = parse_tags(val)
            if tags:
                return tags
    return []


# =========================
# STEP 1 — Dedup: remove 3500 case_references from 7400
# =========================
existing_refs = set(df_3500["case_reference"].astype(str).str.strip())
df_new        = df_7400[
    ~df_7400["case_reference"].astype(str).str.strip().isin(existing_refs)
].copy().reset_index(drop=True)

print(f"\n--- Dedup ---")
print(f"  7400 raw total  : {len(df_7400)}")
print(f"  Overlapping refs: {len(df_7400) - len(df_new)}")
print(f"  Clean candidates: {len(df_new)}")

# =========================
# STEP 2 — Keep only candidates with ≥1 target tag
# =========================
df_new["_case_tags"] = df_new.apply(get_case_tags, axis=1)
df_new["_target_tags_present"] = df_new["_case_tags"].apply(
    lambda tags: [t for t in tags if t in TARGET_TAGS]
)

df_candidates = df_new[df_new["_target_tags_present"].map(len) > 0].copy().reset_index(drop=True)

print(f"\n--- Tag Filter ---")
print(f"  Candidates with ≥1 target tag: {len(df_candidates)}")
print("\n  Target tag frequency in candidates:")
tag_freq = defaultdict(int)
for tags in df_candidates["_target_tags_present"]:
    for t in tags:
        tag_freq[t] += 1
for tag, cnt in sorted(tag_freq.items(), key=lambda x: -x[1]):
    print(f"    {cnt:>4}x  {tag}")

# =========================
# STEP 3 — Encode tag anchors + candidate texts
# =========================
print(f"\n--- Embeddings ---")
print(f"  Loading: {EMBEDDING_MODEL}")
emb_model = SentenceTransformer(EMBEDDING_MODEL)

# Anchor: "TagName. Description of tag."
target_tag_list  = sorted(TARGET_TAGS)
anchor_texts     = [
    f"{t}. {tag_desc_map.get(t, '')}".strip()
    for t in target_tag_list
]

print(f"  Encoding {len(anchor_texts)} tag anchors...")
anchor_embeddings = emb_model.encode(
    anchor_texts, batch_size=32, normalize_embeddings=True, show_progress_bar=False
)

candidate_texts = (
    df_candidates["service"].fillna("").astype(str) + " " +
    df_candidates["summary"].fillna("").astype(str)
).str.strip().tolist()

print(f"  Encoding {len(candidate_texts)} candidate cases...")
candidate_embeddings = emb_model.encode(
    candidate_texts, batch_size=64, normalize_embeddings=True, show_progress_bar=True
)

# =========================
# STEP 4 — Cosine similarity + gate
# =========================
# shape: (n_candidates, n_target_tags)
sim_matrix = cosine_similarity(candidate_embeddings, anchor_embeddings)

tag_to_idx = {t: i for i, t in enumerate(target_tag_list)}

selection_records = []

for i, row in df_candidates.iterrows():
    for tag in row["_target_tags_present"]:
        j         = tag_to_idx[tag]
        sim_score = float(sim_matrix[i, j])
        selection_records.append({
            "case_reference": str(row.get("case_reference", "")),
            "service":        str(row.get("service", "")),
            "summary":        str(row.get("summary", "")),
            "_row_i":         i,
            "_tag":           tag,
            "_sim_score":     sim_score,
            "_passed_gate":   sim_score >= SIM_THRESHOLD,
        })

audit_raw = pd.DataFrame(selection_records)
passed    = audit_raw[audit_raw["_passed_gate"]].copy()

print(f"\n--- Similarity Gate (threshold={SIM_THRESHOLD}) ---")
print(f"  (case, tag) pairs before gate : {len(audit_raw)}")
print(f"  (case, tag) pairs after  gate : {len(passed)}")

# =========================
# STEP 5 — Rank & cap: top N per target tag
# =========================
top_records = (
    passed
    .sort_values("_sim_score", ascending=False)
    .groupby("_tag")
    .head(TOP_N_PER_TAG)
    .reset_index(drop=True)
)

print(f"\n--- Top-{TOP_N_PER_TAG} cap per tag ---")
tag_counts = top_records.groupby("_tag")["case_reference"].count().sort_values(ascending=False)
print(tag_counts.to_string())

# =========================
# STEP 6 — Rebuild rows: one row per case, only target tags retained
# =========================
selected_case_tags   = defaultdict(set)
selected_case_scores = defaultdict(dict)
selected_case_meta   = {}   # store service/summary keyed by case_reference

for _, rec in top_records.iterrows():
    cr = rec["case_reference"]
    selected_case_tags[cr].add(rec["_tag"])
    selected_case_scores[cr][rec["_tag"]] = round(rec["_sim_score"], 4)
    if cr not in selected_case_meta:
        selected_case_meta[cr] = {
            "service": rec["service"],
            "summary": rec["summary"],
        }

new_rows = []
for case_ref, tags in selected_case_tags.items():
    meta       = selected_case_meta[case_ref]
    service    = meta["service"]
    summary    = meta["summary"]
    final_tags = sorted(tags)

    new_rows.append({
        "case_reference":                          case_ref,
        "service":                                 service,
        "summary":                                 summary,
        "final_tags":                              str(final_tags),
        "description_cleaned_tier2_examples_safe": "",
        "description_better_tier2_examples_safe":  "",
        "description_example_safe":                "",
        "cleanlab_input_text_final":               f"{service} {summary}".strip(),
        "sentiment_score":                         None,
        "_source":                                 "new_7400",
        "_sim_scores":                             str(selected_case_scores[case_ref]),
    })

df_new_selected = pd.DataFrame(new_rows)
print(f"\nUnique new cases to append: {len(df_new_selected)}")

# =========================
# STEP 7 — Append to 3500, final dedup safety net, save
# =========================
df_3500_out              = df_3500.copy()
df_3500_out["_source"]   = "original_3500"
df_3500_out["_sim_scores"] = None

# Align columns — fill missing cols in new rows with NaN
all_cols       = list(dict.fromkeys(list(df_3500_out.columns) + list(df_new_selected.columns)))
df_3500_out    = df_3500_out.reindex(columns=all_cols)
df_new_selected = df_new_selected.reindex(columns=all_cols)

df_combined = pd.concat([df_3500_out, df_new_selected], ignore_index=True)
df_combined = df_combined.drop_duplicates(subset=["case_reference"], keep="first")

print(f"\n--- Final Dataset ---")
print(f"  Original 3500 rows : {(df_combined['_source'] == 'original_3500').sum()}")
print(f"  New appended rows  : {(df_combined['_source'] == 'new_7400').sum()}")
print(f"  Total              : {len(df_combined)}")

# =========================
# SAVE
# =========================
df_combined.to_csv(OUT_APPENDED, index=False)

audit_out = top_records[[
    "case_reference", "service", "summary", "_tag", "_sim_score"
]].rename(columns={"_tag": "selected_for_tag", "_sim_score": "similarity_score"})
audit_out.to_csv(OUT_SELECTION_AUDIT, index=False)

print(f"\nSaved: {OUT_APPENDED}")
print(f"Saved: {OUT_SELECTION_AUDIT}")
