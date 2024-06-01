import os
from framework.job_master import *
from framework.config import *
from typing import Callable
from sample.parse_perfanno import *
from sample.parse_perfanno import parse_peranno_txt
import framework.collections

class ExecutionFail(Exception):
    def __init__(self, retval):
        self.retval = retval

    def __str__(self):
        return f"execution failed with return value: {self.retval}"
        
def safesystem(cmd):
    print(f"running command: '{cmd}'")
    res = os.system(cmd)
    if res != 0:
        raise ExecutionFail(res)

def _annotate_and_parse(data_path: str) -> str:
    anno_path = f"{data_path}.annotated"
    safesystem(f"perf annotate --show-total-period --stdio -i {data_path} > {anno_path}")
    print("parsing annotation...")
    with open(anno_path, 'r') as f:
        return parse_peranno_txt(f.read())

class SampleCollector(framework.collections.Collector):
    def get_field_names(self) -> list[str]:
        return [
            "exe_path",
            "thread_count",
            "conf_type"
        ]

    def get_collector(self) -> Callable:
        return _collect_sample

    def create_config(exe_path: str, thread_count: int) -> Config:
        return Config({
            "conf_type": "sample",
            "exe_path": exe_path,
            "thread_count": thread_count,
        })

def _collect_sample(master: JobMaster, config: SampleCollector) -> object:
    data_path = f"{config.exe_path}.tmp.data"
    # safesystem(f"numactl -N 0 perf record {exe_path} && mv perf.data {data_path}")
    exec_cmd = f"{config.exe_path}"
    safesystem(f"OMP_NUM_THREADS={config.thread_count} perf record -ecycles:u,instructions:u -c 100000 {config.exe_path} && mv perf.data {data_path}")
    return _annotate_and_parse(data_path)