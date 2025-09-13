### Compare only incorrect implementations in `implementation_comparison.py`

- **Correctness flag**: Inspect per-sample scores encode correctness via constants in `inspect_ai.scorer._metric`:
  - `CORRECT="C"`, `INCORRECT="I"`, `PARTIAL="P"`, `NOANSWER="N"`.
- **Goal**: Update grouping to include only samples scored as incorrect.
- **Do not implement now**; apply these edits later.

#### 1) Import the INCORRECT flag
```python
from inspect_ai.scorer._metric import INCORRECT
```

#### 2) Filter summaries to only incorrect
Inside `group_samples_by_task(log: EvalLog)`, after reading summaries, add a filter:
```python
summaries: List[EvalSampleSummary] = read_eval_log_sample_summaries(
    log.location or "",
    format="auto",
)

# Keep only incorrect samples
summaries = [
    s for s in summaries
    if s.scores and any(score.value == INCORRECT for score in s.scores.values())
]
```
The rest of the function (grouping into the `groups` dict) remains unchanged.

#### Optional: scorer-agnostic numeric fallback
If you adopt scorers that do not produce categorical C/I/P/N values, you can treat incorrect as a zero-valued score using `value_to_float`:
```python
from inspect_ai.scorer._metric import value_to_float

_to_float = value_to_float()
summaries = [
    s for s in summaries
    if s.scores and any(_to_float(score.value) == 0.0 for score in s.scores.values())
]
```

#### Notes
- This works with `includes()` and `match()` scorers used by the tasks in this repo, which set `Score.value` to `"C"` or `"I"` via the common string-match scorer.
- No CLI changes are required; the comparison tool will simply process a smaller set (only incorrect samples).