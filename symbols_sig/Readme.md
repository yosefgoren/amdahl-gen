## Symbols Significant
A collection of type 'symbols-sig' describes an aggregation of symbols - in the sense that multiple symbols with the same setting are combined to create a result
which is more statistically significant - meaning it's not as effected by randomness or noise.

### Collector
The collector follows these steps:
* `A.symbols-sig.config.json` -> `A.sample.config.json`: Create a symbols configuration based on the significant configuration.
* `A.symbols.config.json` -> `[A.symbols.result.json]`: Run the symbols collector many times to get a set of results.
* `[A.sample.result.json]` -> `A.result.json`: Aggregate the symbols results to a significant result.

### Result
Results of this collection correspond each source code line with the average time it took to run, this average is over both the many times the line was executed in each sample, and also over the many samples in which it was executed.
The results will follow the [symbols-sig results schema](symbols_sig.result.schema.json)
