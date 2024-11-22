## Alpha
A collection of type 'alpha' describes a property of the executable for each lines in the source code.
This 'alpha' property is meant to describe the parallelizability of this line of the source code.
More speicifically 'alpha' is the 'proportion' of this line which is parallelizable.

### Configuration
[The configuration schema](schemas/alpha.config.schema.json) requires a list of thread counts which will be used to evaluate alpha,
and a repetition count which determines how many times each thread count sample should be taken.

### Collector
The collector follows these steps:
* `A.alpha.config.json` -> `[A.significat.config.json]`: Create a set of collection configs of type 'significant', based on the provided configuration and with a variable number of threads.
* `[A.significat.config.json]` -> `[A.significant.result.json]`: Run the significant collector over each of the configurations to get a list of results.
* `[A.significant.result.json]` -> `A.alpha.result.json`: Aggregate the list of results by finding a best fit trendline and using it's parameter value as alpha.

### Result
Results associate each source line with an alpha value and follow the [alpha results schema](schemas/alpha.result.schema.json).