# Evaluation baselines

Baselines store aggregated scenario and capability quality, pass rate, duration, and observable token counts.
They are dynamic last-green measurements and never replace version-controlled Golden expectations.

Compare a current run without changing the baseline:

```bash
python3 tools/evals/compare_baseline.py \
  --current output/eval-results/performance.json \
  --baseline evals/baselines/v1.0.0.json \
  --output output/eval-results/baseline-comparison.json
```

The checked-in `v1.0.0.json` remains `bootstrap` until a real accepted run exists. Comparisons against a
bootstrap or empty baseline report `NOT_AVAILABLE`; they never claim a green comparison.

Promote only an explicitly accepted, warning-free nightly run whose report records `main`:

```bash
python3 tools/evals/promote_baseline.py \
  --run-dir output/eval-results \
  --accepted-run nightly-2030-01-15 \
  --branch main \
  --output evals/baselines/v1.0.0.json
```

The ordinary evaluation runner and PR pipeline cannot promote or rewrite the last-green baseline. Timing and
token comparisons use relative warning/failure tolerances and noise floors. Quality regressions remain stricter.
