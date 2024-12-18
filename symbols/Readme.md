## Sample
A collection of type 'sample' describes a single run of a program, in a specific setting.
This is an atomic collection type meaning it's results don't require any other collection results to be created.

### Configuration
[The configuration schema](symbols.config.schema.json) requires providing a path to a target executable,
and the number of threads on which this sample should run.

### Collector
The collector follows these steps:
* `A.sample.config.json` -> `perf.data`: Use `perf record` to collect raw binary data.
* `perf.data` -> `anno.txt`: Use `perf annotate` to turn the binary data to textual.
* `anno.txt` -> `A.sample.result.json`: Use `parse_perfanno.py` to parse the textual data to the required output format.

### Result
[The result schema](symbols.result.schema.json) requires the result will be a list of lines and their corresponding runtimes, and execution counts (the numebr of times the line was executed).
