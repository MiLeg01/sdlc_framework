# ADM estimation model

For each calibration source record owner, date, actual work population, effort unit, inclusions, team profile,
target technology, delivery quality bar, normalization, and applicability. Use `UNAVAILABLE` rather than
fabricating a rate. Uncalibrated estimates are rough-order-of-magnitude and require LOW confidence.

For every work unit record:

- `optimistic`: a credible favorable execution path;
- `mostLikely`: effort under the stated assumptions;
- `pessimistic`: a credible adverse path covering named uncertainty;
- `expected`: `(optimistic + 4 * mostLikely + pessimistic) / 6`, calculated by the bundled tool.

Summed endpoints are scenario bounds, not statistical confidence intervals. Correlated risks make naive
variance assumptions unsafe. Preserve asymmetric ranges where evidence warrants them.

Never multiply source lines or counts by an invented productivity constant, apply uncalibrated complexity
multipliers, transfer another application's counts or ratings, hide delivery work inside functional units,
add blanket contingency for risks already in the range, or convert effort to cost without explicit role mix,
rates, location, currency, and date. Round totals to precision supported by the weakest material input.
