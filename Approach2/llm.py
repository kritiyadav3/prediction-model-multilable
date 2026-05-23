import re
import json
import ast
import pandas as pd
from collections import Counter, defaultdict
from openai import AzureOpenAI

# =========================
# CONFIG
# =========================
FINAL_CASE_PATH = "./builtin/final_case_tag_qc_detailed_report (1).csv"
TIER2_DESC_PATH = "./builtin/Tier2_tier_description.csv"

OUT_FINAL = "saved_data/final_training_dataset_llm_validated_noleak.csv"
OUT_AUDIT = "saved_data/final_case_decision_audit_llm.csv"
OUT_METRICS = "saved_data/final_metrics_llm_selection.csv"

LLM_CONF_KEEP = 0.60
LLM_CONF_PROMOTE = 0.70
MAX_BETTER_TAGS = 10

client = AzureOpenAI(
    api_version=az_openai_api_version,
    azure_endpoint=az_openai_endpoint,
    api_key=az_openai_key,
)
DEPLOYMENT = az_openai_deployment

# =========================
# LOAD
# =========================
final_case = pd.read_csv(FINAL_CASE_PATH)
tier2_desc = pd.read_csv(TIER2_DESC_PATH)

cols_lower = {c.lower(): c for c in tier2_desc.columns}
tag_col = cols_lower.get("Tier 2", list(tier2_desc.columns)[0])
desc_col = cols_lower.get("Tier2_description", list(tier2_desc.columns)[1])

tag_desc_map = {
    str(r[tag_col]).strip(): str(r[desc_col]).strip()
    for _, r in tier2_desc.iterrows()
    if str(r[tag_col]).strip()
}

# =========================
# HELPERS
# =========================
def parse_tag_block(s):
    if pd.isna(s):
        return []
    s = str(s).strip()
    if not s:
        return []

    items = []
    pattern = r"([^,]+?)\s*\(q=([0-9.]+)(?:,\s*thr=([0-9.]+))?(?:,\s*noise=([0-9.]+)%?)?\)"
    matches = re.findall(pattern, s)

    if matches:
        for m in matches:
            tag = m[0].strip()
            q = float(m[1]) if m[1] else None
            thr = float(m[2]) if m[2] else None
            noise = float(m[3]) / 100.0 if m[3] else (1.0 - q if q is not None else None)
            items.append({"tag": tag, "q": q, "thr": thr, "noise": noise})
        return items

    for part in s.split(","):
        t = part.strip()
        if t:
            items.append({"tag": t, "q": None, "thr": None, "noise": None})
    return items


def simple_sentiment_score(text):
    text = str(text).lower()
    pos_words = ["resolved", "helpful", "fixed", "happy", "satisfied", "good", "clear"]
    neg_words = ["frustrated", "angry", "unfair", "charged", "dispute", "delay", "poor", "complaint", "issue", "problem", "disconnect"]

    p = sum(w in text for w in pos_words)
    n = sum(w in text for w in neg_words)

    if p + n == 0:
        return 0.0
    return (p - n) / (p + n)


def sanitize_no_label_leakage(text, tags):
    out = str(text)
    for t in sorted(set(tags), key=len, reverse=True):
        if not t:
            continue

        out = re.sub(re.escape(t), "this issue type", out, flags=re.IGNORECASE)

        for part in re.split(r"[/,()-]", t):
            part = part.strip()
            if len(part) >= 4:
                out = re.sub(r"\b" + re.escape(part) + r"\b", "issue", out, flags=re.IGNORECASE)

    out = re.sub(r"\s+", " ", out).strip()
    return out


SYSTEM_PROMPT = """
You are a senior telecom complaint labeling auditor for multi-label training data.

Objective:
Select the best final label set for one complaint using semantic evidence and score evidence.

Inputs include:
- service
- complaint summary
- candidate labels with quality score, threshold, noise
- sentiment score

Rules:
1) Keep labels that are semantically supported by summary and service.
2) Recover dropped labels only if semantic evidence is strong and score is near threshold.
3) Promote better labels only if clearly more accurate than dropped labels.
4) Be cautious adding labels with weak evidence.
5) Prefer preserving rare or medium labels if semantically valid and only slightly below threshold.

Output strict JSON only with schema:
{
  "final_tags": ["..."],
  "decisions": [
    {"tag":"...", "decision":"KEEP|DROP|PROMOTE|RECOVER|REJECT", "confidence":0.0, "reason":"..."}
  ],
  "description_cleaned_tier2_examples":"...",
  "description_better_tier2_examples":"..."
}

IMPORTANT:
In description fields, do not include explicit label names.
Do not copy label strings.
"""


def llm_decide(service, summary, candidates, sentiment):
    payload = {
        "service": service,
        "summary": summary,
        "sentiment_score": sentiment,
        "candidates": candidates
    }

    resp = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )

    return json.loads(resp.choices[0].message.content)


# =========================
# MAIN
# =========================
final_rows = []
audit_rows = []

before_counter = Counter()
after_counter = Counter()

for _, r in final_case.iterrows():
    case_reference = r.get("case_reference", "")
    service = str(r.get("service", ""))
    summary = str(r.get("summary", ""))

    old_tags = [x["tag"] for x in parse_tag_block(r.get("tier2", ""))]
    cleaned = parse_tag_block(r.get("tier2_cleaned", ""))
    dropped = parse_tag_block(r.get("tier2_dropped", ""))
    better = parse_tag_block(r.get("better_tier2", ""))[:MAX_BETTER_TAGS]

    for t in old_tags:
        before_counter[t] += 1

    dropped_max_q = max([x["q"] for x in dropped if x["q"] is not None], default=None)

    filtered_better = []
    for b in better:
        if dropped_max_q is None:
            continue
        if b["q"] is not None and b["q"] > dropped_max_q:
            filtered_better.append(b)

    candidates = []

    for x in cleaned:
        candidates.append({
            "tag": x["tag"],
            "source": "cleaned",
            "quality_score": x["q"],
            "threshold": x["thr"],
            "noise": x["noise"],
            "description": tag_desc_map.get(x["tag"], "")
        })

    for x in dropped:
        candidates.append({
            "tag": x["tag"],
            "source": "dropped",
            "quality_score": x["q"],
            "threshold": x["thr"],
            "noise": x["noise"],
            "description": tag_desc_map.get(x["tag"], "")
        })

    for x in filtered_better:
        candidates.append({
            "tag": x["tag"],
            "source": "better",
            "quality_score": x["q"],
            "threshold": x["thr"],
            "noise": x["noise"],
            "description": tag_desc_map.get(x["tag"], "")
        })

    sentiment = simple_sentiment_score(summary)

    try:
        out = llm_decide(service, summary, candidates, sentiment)
    except Exception as e:
        out = {
            "final_tags": [c["tag"] for c in candidates if c["source"] == "cleaned"],
            "decisions": [
                {
                    "tag": c["tag"],
                    "decision": "KEEP" if c["source"] == "cleaned" else "REJECT",
                    "confidence": 0.0,
                    "reason": f"fallback due to llm error: {str(e)}"
                }
                for c in candidates
            ],
            "description_cleaned_tier2_examples": "",
            "description_better_tier2_examples": ""
        }

    final_tags = out.get("final_tags", [])
    if not isinstance(final_tags, list):
        final_tags = []

    decision_map = {
        d.get("tag"): d for d in out.get("decisions", [])
        if isinstance(d, dict)
    }

    gated_tags = []
    for t in final_tags:
        d = decision_map.get(t, {})
        conf = float(d.get("confidence", 0.0) or 0.0)
        dec = str(d.get("decision", "")).upper()

        if dec in ["KEEP", "RECOVER"] and conf >= LLM_CONF_KEEP:
            gated_tags.append(t)
        elif dec == "PROMOTE" and conf >= LLM_CONF_PROMOTE:
            gated_tags.append(t)

    final_tags = list(dict.fromkeys(gated_tags))

    for t in final_tags:
        after_counter[t] += 1

    desc_clean = str(out.get("description_cleaned_tier2_examples", ""))
    desc_better = str(out.get("description_better_tier2_examples", ""))

    noleak_tags = [c["tag"] for c in candidates]

    desc_clean_safe = sanitize_no_label_leakage(desc_clean, noleak_tags)
    desc_better_safe = sanitize_no_label_leakage(desc_better, noleak_tags)

    description_example_safe = " [SEP] ".join(
        [x for x in [desc_clean_safe, desc_better_safe] if x]
    ).strip()

    train_text = f"{service} {summary} {description_example_safe}".strip()

    final_rows.append({
        "case_reference": case_reference,
        "service": service,
        "summary": summary,
        "final_tags": str(final_tags),
        "description_cleaned_tier2_examples_safe": desc_clean_safe,
        "description_better_tier2_examples_safe": desc_better_safe,
        "description_example_safe": description_example_safe,
        "cleanlab_input_text_final": train_text,
        "sentiment_score": sentiment
    })

    for c in candidates:
        d = decision_map.get(c["tag"], {})
        audit_rows.append({
            "case_reference": case_reference,
            "service": service,
            "summary": summary,
            "tag": c["tag"],
            "source": c["source"],
            "quality_score": c["quality_score"],
            "threshold": c["threshold"],
            "noise": c["noise"],
            "sentiment_score": sentiment,
            "decision": d.get("decision", ""),
            "confidence": d.get("confidence", ""),
            "reason": d.get("reason", "")
        })

final_df = pd.DataFrame(final_rows)
audit_df = pd.DataFrame(audit_rows)

# =========================
# METRICS
# =========================
metric_rows = []

tags_all = set(before_counter.keys()) | set(after_counter.keys())

for t in sorted(tags_all):
    b = before_counter.get(t, 0)
    a = after_counter.get(t, 0)

    metric_rows.append({
        "tag": t,
        "before_count": b,
        "after_count": a,
        "coverage_change": a - b,
        "coverage_change_pct": ((a - b) / b) if b > 0 else None
    })

promote_count = (audit_df["decision"].astype(str).str.upper() == "PROMOTE").sum()
recover_count = (audit_df["decision"].astype(str).str.upper() == "RECOVER").sum()
keep_count = (audit_df["decision"].astype(str).str.upper() == "KEEP").sum()
drop_count = (audit_df["decision"].astype(str).str.upper() == "DROP").sum()

metric_rows.extend([
    {"tag": "__GLOBAL__", "before_count": len(final_case), "after_count": len(final_df), "coverage_change": len(final_df) - len(final_case), "coverage_change_pct": None},
    {"tag": "__DECISION_KEEP__", "before_count": None, "after_count": keep_count, "coverage_change": None, "coverage_change_pct": None},
    {"tag": "__DECISION_DROP__", "before_count": None, "after_count": drop_count, "coverage_change": None, "coverage_change_pct": None},
    {"tag": "__DECISION_PROMOTE__", "before_count": None, "after_count": promote_count, "coverage_change": None, "coverage_change_pct": None},
    {"tag": "__DECISION_RECOVER__", "before_count": None, "after_count": recover_count, "coverage_change": None, "coverage_change_pct": None},
])

metrics_df = pd.DataFrame(metric_rows)

# =========================
# SAVE
# =========================
final_df.to_csv(OUT_FINAL, index=False)
audit_df.to_csv(OUT_AUDIT, index=False)
metrics_df.to_csv(OUT_METRICS, index=False)

print("Saved:", OUT_FINAL)
print("Saved:", OUT_AUDIT)
print("Saved:", OUT_METRICS)
print("Rows final:", len(final_df))
print("Rows audit:", len(audit_df))
