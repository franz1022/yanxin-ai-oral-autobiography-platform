# Memory Extraction Evaluation

## 1. Purpose

This document evaluates Yanxin's bilingual, rule-based memory extraction workflow.

The extractor converts a Chinese or English memory passage into reviewable life-event fields:

- detected language;
- event title;
- start and end year;
- date certainty;
- location;
- people involved;
- emotional tone.

The system does **not** save extracted fields automatically. Every result remains subject to human review and editing before it can be written to the life timeline.

---

## 2. Evaluation Design

### 2.1 Development benchmark

A bilingual development benchmark was created with:

- 24 fictional cases;
- 12 Chinese cases;
- 12 English cases;
- easy, medium and hard examples;
- manually labelled target fields.

The development benchmark was used to:

1. establish a baseline;
2. identify systematic errors;
3. improve title generation and location boundary rules;
4. run regression checks.

Because this benchmark was used during rule development, its final score is **not** treated as an independent generalisation result.

### 2.2 Frozen holdout benchmark

A separate frozen holdout benchmark was created with:

- 20 new fictional cases;
- 10 Chinese cases;
- 10 English cases;
- no exact text overlap with the development benchmark;
- labels frozen before the first formal evaluation.

The extraction rules were frozen at commit:

```text
0169ccd
```

The holdout benchmark was committed before evaluation. Its SHA-256 hash is:

```text
6bab95361b099280fa994ddca6cf2b13f265f11e5399feca5a5a36d4794cb47e
```

The formal holdout evaluation was executed from Git HEAD:

```text
1f9a7abd552685a16c8eca710e48f33a9cb831cb
```

The holdout protocol is one-shot:

- report the result once;
- do not tune extraction rules against these cases;
- preserve the result as the independent estimate of prototype generalisation.

---

## 3. Development Benchmark Results

### 3.1 Baseline before targeted rule improvement

| Metric | Result |
|---|---:|
| Core-field micro accuracy | 95.00% |
| Core complete-record accuracy | 75.00% |
| All-field micro accuracy | 90.10% |
| Language detection accuracy | 100.00% |
| Human-review flag rate | 100.00% |
| Event-title accuracy | 45.83% |
| Location accuracy | 75.00% |

Initial error analysis showed two main weaknesses:

1. **Title compression** — the extractor often returned a full sentence instead of a short event title.
2. **Location boundaries** — the extractor sometimes included action text after the location.

Examples included:

```text
Expected: 深圳
Predicted: 深圳举行婚礼
```

and:

```text
Expected: 庆祝毕业
Predicted: 我在北京生活，和朋友一起庆祝毕业，我们非常开心
```

### 3.2 Development result after targeted rule improvement

After improving title templates and location-boundary rules:

| Metric | Result |
|---|---:|
| Core-field micro accuracy | 100.00% |
| Core complete-record accuracy | 100.00% |
| All-field micro accuracy | 100.00% |
| Event-title accuracy | 100.00% |
| Location accuracy | 100.00% |

These values describe performance on the same development benchmark used for error analysis and rule refinement. They demonstrate that the identified development errors were addressed, but they do **not** establish production-level or out-of-sample performance.

---

## 4. Independent Holdout Results

### 4.1 Overall results

| Metric | Holdout result |
|---|---:|
| Core-field micro accuracy | **91.00%** |
| Core complete-record accuracy | **55.00%** |
| All-field micro accuracy | **86.87%** |
| Language detection accuracy | **100.00%** |
| Human-review flag rate | **100.00%** |

The difference between field-level accuracy and complete-record accuracy is expected: a record is counted as completely correct only when every evaluated core field matches its label.

### 4.2 Field-level results

| Field | Group | Accuracy |
|---|---|---:|
| Detected language | Supporting | 100.00% |
| Event title | Supporting | 40.00% |
| Date certainty | Supporting | 100.00% |
| Start year | Core | 100.00% |
| End year | Core | 100.00% |
| Location | Core | 70.00% |
| People involved | Core | 90.00% |
| Emotional tone | Core | 95.00% |

The most reliable fields were:

- language;
- start year;
- end year;
- date certainty.

The weakest fields were:

- generated event title;
- location boundary extraction.

### 4.3 Language-level results

| Language | Cases | Average core-field accuracy | Core complete-record accuracy | Average all-field accuracy |
|---|---:|---:|---:|---:|
| English | 10 | 94.00% | 70.00% | 88.75% |
| Chinese | 10 | 88.00% | 40.00% | 85.00% |

The holdout set suggests stronger performance on English core fields than Chinese core fields. Because each language group contains only 10 examples, this difference should be treated as an exploratory signal rather than a stable population estimate.

---

## 5. Holdout Error Analysis

### 5.1 Event title

Event-title accuracy was 40.00%.

Many strict mismatches were semantically related but differed in compression or wording.

Examples:

```text
Expected: 与姐姐在杭州看烟花
Predicted: 我和姐姐在杭州看烟花
```

```text
Expected: Watching Fireworks in Hangzhou
Predicted: 1984, I watched fireworks in Hangzhou with my older sister
```

This confirms that generated titles should remain editable drafts rather than final metadata.

### 5.2 Location

Location accuracy was 70.00%.

Most errors were boundary errors in which an action was included after the location.

Examples:

```text
Expected: 杭州
Predicted: 杭州看烟花
```

```text
Expected: 南京
Predicted: 南京读中学
```

```text
Expected: 家乡的厨房
Predicted: 家乡的厨房里做饭
```

The extractor often identifies the relevant region of text correctly but does not always stop at the correct semantic boundary.

### 5.3 People involved

People accuracy was 90.00%.

One recurring issue came from substring matching:

```text
Expected: Storyteller and grandmother
Predicted: Storyteller, grandmother, mother
```

The term `mother` was incorrectly detected inside `grandmother`. This is a typical limitation of simple string-based rules.

### 5.4 Emotional tone

Emotional-tone accuracy was 95.00%.

One joyful example was classified as reflective, showing that indirect emotional language is not always covered by the current keyword rules.

---

## 6. Interpretation

The holdout results support the following conclusions:

1. The extractor is a useful **local, interpretable prototype baseline**.
2. Explicit temporal fields generalise well in the current fictional benchmark.
3. People and emotional tone are reasonably stable but still require review.
4. Event titles and location boundaries remain the main sources of error.
5. Human review is a necessary product control, not a cosmetic interface step.

The appropriate product role is therefore:

```text
memory passage
→ local structured draft
→ confidence display
→ human correction
→ confirmed life-event record
```

The extractor should not be presented as an autonomous factual-record creation system.

---

## 7. Model-Governance Decision

The project deliberately keeps:

```text
review_required = True
```

for every extracted case.

The prototype does not:

- automatically approve extracted facts;
- automatically write unreviewed content into the timeline;
- claim that generated titles are final;
- claim production-level accuracy;
- send memories to an external model in the default public-demo workflow.

The optional LLM provider remains registered but disabled. The public prototype uses the local rule-based provider.

---

## 8. Limitations

This evaluation has several important limitations:

- all cases are fictional;
- the development benchmark contains only 24 cases;
- the independent holdout contains only 20 cases;
- the benchmark does not cover dialects, speech-recognition errors, very long narratives or real private materials;
- strict string matching can mark semantically similar titles as incorrect;
- rule-based patterns may not generalise to unseen sentence structures;
- no production user study has been conducted.

Accordingly, the reported holdout accuracy is a prototype evaluation result, not a production performance guarantee.

---

## 9. Reproducibility

Run the development evaluation:

```powershell
python -m scripts.evaluate_memory_extractor
```

Run the development evaluation tests:

```powershell
python -m scripts.test_memory_extractor_evaluation
```

Check holdout integrity:

```powershell
python -m scripts.test_memory_extractor_holdout
```

Run the one-shot holdout evaluation:

```powershell
python -m scripts.evaluate_memory_extractor_holdout
```

Development outputs are written to:

```text
outputs/evaluation
```

Holdout outputs are written to:

```text
outputs/evaluation/holdout
```

---

## 10. Portfolio Summary

A concise and defensible project summary is:

> A bilingual, privacy-aware oral-history workflow that converts memory passages into reviewable structured life events. A 24-case development benchmark was used for error analysis and rule improvement. After freezing the extraction rules, a one-shot evaluation on 20 unseen fictional holdout cases achieved 91% core-field micro accuracy and 55% complete-record accuracy. Results showed strong year extraction but weaker title compression and location boundaries, supporting the decision to require human review before saving.
