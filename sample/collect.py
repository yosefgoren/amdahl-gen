import json, jsonschema
from impl.parse_perfanno import *

def perf_exec(exe_path: str) -> str:
    pass

def annotate_and_parse(data_path) -> str:
    pass

def collect_sample(config: object) -> object:
    jsonschema.validate(config, json.load(open("sample.config.schema.json")))

    output_path = perf_exec(config["exe-path"])

    return annotate_and_parse(output_path)