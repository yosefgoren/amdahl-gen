## Srcliesn Significant
A collection of type 'srclines_sig' describes an aggregation of srclines - in the sense that multiple samples with the same setting are combined to create a result
which is more statistically significant - meaning it's not as effected by randomness or noise.

### Collector
The collector follows these steps:
* `A.srclines.config.json` -> `A.samsrclinesple.config.json`: Create a srclines configuration based on the significant configuration.
* `A.srclines.config.json` -> `[A.srclines.result.json]`: Run the srclines collector many times to get a set of results.
* `[A.srclines.result.json]` -> `A.result.json`: Aggregate the srclines results to a significant result.

### Result
Results of this collection correspond each source code line with the average time it took to run, this average is over both the many times the line was executed in each samples, and also over the many samples in which it was executed.
The results will follow the [significant results schema](srclines_sig.result.schema.json)
