# Data

There is one folder per function:

```
data/function_N/
|-- initial_inputs.npy    # (n0, d) supplied design (course-provided, never modified)
|-- initial_outputs.npy   # (n0,)   its observed values
`-- observations.csv      # one row per graded weekly query: x1..xd, y (9 rows; append-only)
```

`bbo.data.load(data_dir, N)` returns the supplied points and the
observations stacked together.

The week-10 queries are in `results/query_log.csv`, with the `observed`
column left blank until the portal returns results. Provenance and
composition are documented in `../datasheets/`.
