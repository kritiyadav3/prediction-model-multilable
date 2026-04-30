Here are the complete updated blocks 9 through 12 with everything integrated:

***

## Block 9 — Model + BCE Loss + Optimiser

```python
# ── BLOCK 9: MODEL + BCE LOSS + OPTIMISER ─────────────────────────

RUN_NAME = "bce_logistic"   # ← all outputs saved with this prefix

class ComplaintTagger(nn.Module):
    def __init__(self):
        super().__init__()
        self.bert       = AutoModel.from_pretrained(MODEL_NAME)
        self.dropout    = nn.Dropout(0.3)
        self.classifier = nn.Linear(self.bert.config.hidden_size, NUM_LABELS)

    def forward(self, input_ids, attention_mask):
        out    = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled = self.dropout(out.last_hidden_state[:, 0])   # CLS token
        return self.classifier(pooled)                        # raw logits — NO sigmoid here


# ── POS_WEIGHT: per-tag imbalance correction ──────────────────────
tag_pos_counts = torch.tensor(y_tr.sum(axis=0),               dtype=torch.float32)
tag_neg_counts = torch.tensor(len(y_tr) - y_tr.sum(axis=0),   dtype=torch.float32)
pos_weight     = (tag_neg_counts / tag_pos_counts.clamp(min=1)).clamp(max=10).to(DEVICE)

print(f"pos_weight → min={pos_weight.min():.2f}  max={pos_weight.max():.2f}  mean={pos_weight.mean():.2f}")


# ── BCE LOSS ──────────────────────────────────────────────────────
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight, reduction='mean')


# ── MODEL ─────────────────────────────────────────────────────────
model     = ComplaintTagger().to(DEVICE)
optimizer = AdamW(model.parameters(), lr=LR, weight_decay=0.01)

total_steps  = len(train_loader) * EPOCHS
warmup_steps = max(1, total_steps // 6)    # longer warmup for small dataset

scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=warmup_steps,
    num_training_steps=total_steps
)

total_params = sum(p.numel() for p in model.parameters())
print(f"Run:      {RUN_NAME}")
print(f"Model:    {total_params:,} params  |  Device: {DEVICE}")
print(f"Loss:     BCEWithLogitsLoss  |  pos_weight clamped at 10")
print(f"LR:       {LR}  |  Warmup: {warmup_steps} steps  |  Total: {total_steps} steps")
print(f"Epochs:   {EPOCHS}  |  Batch: {BATCH_SIZE}  |  Early stop patience: {EARLY_STOP_PAT}")
```

***

## Block 10 — Training Loop

```python
# ── BLOCK 10: TRAINING LOOP ───────────────────────────────────────

def train_epoch(model, loader):
    model.train()
    total = 0
    for b in tqdm(loader, desc='Train', leave=False):
        optimizer.zero_grad()
        logits = model(
            b['input_ids'].to(DEVICE),
            b['attention_mask'].to(DEVICE)
        )
        loss = criterion(logits, b['labels'].to(DEVICE))
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        total += loss.item()
    return total / len(loader)


def eval_epoch(model, loader):
    model.eval()
    probs_all, labels_all = [], []
    with torch.no_grad():
        for b in tqdm(loader, desc='Eval', leave=False):
            logits = model(
                b['input_ids'].to(DEVICE),
                b['attention_mask'].to(DEVICE)
            )
            probs_all.append(torch.sigmoid(logits).cpu().numpy())   # sigmoid applied HERE
            labels_all.append(b['labels'].numpy())
    return np.vstack(probs_all), np.vstack(labels_all)


print(f"Training {RUN_NAME}  |  max {EPOCHS} epochs  |  patience {EARLY_STOP_PAT}")
best_f1, pat = 0.0, 0
history = []

for epoch in range(EPOCHS):
    print(f"\nEpoch {epoch+1}/{EPOCHS}")
    tl              = train_epoch(model, train_loader)
    vp, vl          = eval_epoch(model, val_loader)
    vlh             = (vl > 0.5).astype(int)
    macro           = f1_score(vlh, (vp > 0.5).astype(int), average='macro',  zero_division=0)
    micro           = f1_score(vlh, (vp > 0.5).astype(int), average='micro',  zero_division=0)

    # monitor at lower threshold to see real learning in early epochs
    macro_30        = f1_score(vlh, (vp > 0.3).astype(int), average='macro',  zero_division=0)

    history.append({'epoch': epoch+1, 'loss': round(tl,4),
                    'macro_f1': round(macro,4), 'micro_f1': round(micro,4),
                    'macro_f1_thr30': round(macro_30,4)})

    print(f"  Loss: {tl:.4f}  |  Val Macro F1 (0.5): {macro:.4f}  |  Val Micro F1: {micro:.4f}")
    print(f"  Val Macro F1 (0.3 thr — early signal): {macro_30:.4f}")

    # ── Save every epoch checkpoint ──
    torch.save({
        'epoch':           epoch + 1,
        'model_state':     model.state_dict(),
        'optimizer_state': optimizer.state_dict(),
        'macro_f1':        macro
    }, f'checkpoints/{RUN_NAME}_epoch{epoch+1}.pt')

    # ── Save best model ──
    if macro > best_f1:
        best_f1 = macro
        torch.save(model.state_dict(), f'checkpoints/{RUN_NAME}_best_model.pt')
        print(f"  ✓ Best model saved → checkpoints/{RUN_NAME}_best_model.pt")
        pat = 0
    else:
        pat += 1
        print(f"  No improvement. Patience: {pat}/{EARLY_STOP_PAT}")
        if pat >= EARLY_STOP_PAT:
            print(f"\n  Early stop. Best Val Macro F1: {best_f1:.4f}")
            break

pd.DataFrame(history).to_csv(f'saved_data/{RUN_NAME}_training_history.csv', index=False)
print(f"\nDone. Best Val Macro F1: {best_f1:.4f}")
print(f"Saved: checkpoints/{RUN_NAME}_best_model.pt")
print(f"Saved: saved_data/{RUN_NAME}_training_history.csv")
```

***

## Block 11 — Per-Tag Threshold Tuning

```python
# ── BLOCK 11: PER-TAG THRESHOLD TUNING ────────────────────────────

print(f"Loading {RUN_NAME} best model for threshold tuning...")
model.load_state_dict(
    torch.load(f'checkpoints/{RUN_NAME}_best_model.pt', map_location=DEVICE)
)

vp, vl    = eval_epoch(model, val_loader)
vlh       = (vl > 0.5).astype(int)
tag_freq  = y_tr.sum(axis=0) / len(y_tr)
thresholds = []

for i in range(NUM_LABELS):
    best_t, best_f = 0.5, 0.0
    for t in np.arange(0.10, 0.91, 0.05):
        f = f1_score(vlh[:, i], (vp[:, i] > t).astype(int), zero_division=0)
        if f > best_f:
            best_f, best_t = f, t
    if tag_freq[i] > DOMINANT_FREQ:
        best_t = max(best_t, 0.65)     # stop over-predicting dominant tags
    if tag_freq[i] < RARE_FREQ:
        best_t = min(best_t, 0.35)     # ensure rare tags can fire
    thresholds.append(best_t)

thresholds = np.array(thresholds)

thr_df = pd.DataFrame({
    'tag':        valid_tags,
    'train_freq': (tag_freq * 100).round(1),
    'threshold':  thresholds,
    'category':   ['dominant' if f > DOMINANT_FREQ else
                   'rare'     if f < RARE_FREQ else 'normal'
                   for f in tag_freq]
}).sort_values('train_freq', ascending=False)

np.save(f'saved_data/{RUN_NAME}_tag_thresholds.npy', thresholds)
thr_df.to_csv(f'saved_data/{RUN_NAME}_tag_info.csv', index=False)

# show val F1 before vs after threshold tuning
macro_before = f1_score(vlh, (vp > 0.5).astype(int), average='macro', zero_division=0)
macro_after  = f1_score(vlh, (vp > thresholds).astype(int), average='macro', zero_division=0)

print(f"Val Macro F1 — global 0.5:      {macro_before:.4f}")
print(f"Val Macro F1 — per-tag tuned:   {macro_after:.4f}")
print(f"Lift from threshold tuning:     +{macro_after - macro_before:.4f}")
print(f"\nSaved: saved_data/{RUN_NAME}_tag_thresholds.npy")
print(f"Saved: saved_data/{RUN_NAME}_tag_info.csv")
print(thr_df.to_string(index=False))
```

***

## Block 12 — Final Test Evaluation

```python
# ── BLOCK 12: FINAL TEST EVALUATION ───────────────────────────────

print(f"Running final test evaluation for: {RUN_NAME}")
model.load_state_dict(
    torch.load(f'checkpoints/{RUN_NAME}_best_model.pt', map_location=DEVICE)
)
thresholds = np.load(f'saved_data/{RUN_NAME}_tag_thresholds.npy')

tp, tl   = eval_epoch(model, test_loader)
tlh      = (tl > 0.5).astype(int)
preds    = (tp > thresholds).astype(int)

macro_test  = f1_score(tlh, preds, average='macro',   zero_division=0)
micro_test  = f1_score(tlh, preds, average='micro',   zero_division=0)
samp_test   = f1_score(tlh, preds, average='samples', zero_division=0)

print("=" * 55)
print(f"Run:       {RUN_NAME}")
print(f"Macro F1:  {macro_test:.4f}   ← primary metric")
print(f"Micro F1:  {micro_test:.4f}")
print(f"Samples F1:{samp_test:.4f}")
print("=" * 55)
print(classification_report(tlh, preds, target_names=valid_tags, zero_division=0))

# ── Save predictions ──
pred_df = df_te[['case_reference']].copy()
for i, tag in enumerate(valid_tags):
    pred_df[f'pred_{tag}']  = preds[:, i]
    pred_df[f'prob_{tag}']  = tp[:, i].round(3)
pred_df.to_csv(f'saved_data/{RUN_NAME}_test_predictions.csv', index=False)

print(f"\nSaved: saved_data/{RUN_NAME}_test_predictions.csv")
```

***

Your output folder will now have:

```
checkpoints/
  ├── bce_logistic_best_model.pt
  └── bce_logistic_epoch1.pt  (one per epoch)

saved_data/
  ├── bce_logistic_training_history.csv
  ├── bce_logistic_tag_thresholds.npy
  ├── bce_logistic_tag_info.csv
  └── bce_logistic_test_predictions.csv
```

All previous ASL run files stay untouched. Run Block 9 → 10 → 11 → 12 in order.

Sources
