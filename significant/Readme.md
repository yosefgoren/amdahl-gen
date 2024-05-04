## Significant
A collection of type 'significant' describes an aggregation of samples - in the sense that multiple samples with the same setting are combined to create a result
which is more statistically significant - meaning it's not as effected by randomness or noise.

### Collector
The collector follows these steps:
* `A.significant.config.json` -> `A.sample.config.json`: Create a sample configuration based on the significant configuration.
* `A.sample.config.json` -> `[A.sample.result.json]`: Run the sample collector many times to get a set of results.
* `[A.sample.result.json]` -> `A.result.json`: Aggregate the sample results to a significant result.

### Result
Results of this collection correspond each source code line with the average time it took to run, this average is over both the many times the line was executed in each sample, and also over the many samples in which it was executed.
The results will follow the [significant results schema](schemas/significant.result.schema.json)
