import os
from framework.job_master import *
from framework.config import *
from typing import Callable
import framework.collections

"""
This refers to the perf-report option:
    -c, --count=
        Event period to sample.
"""
EVENTS_PER_SAMPLE = 5000

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

def _report_and_parse(exe_path: str, data_path: str) -> str:
    # generate the report:
    report_path = f"{data_path}.report"
    safesystem(f"perf report -d {list(exe_path.split('/'))[-1]} -i {data_path} -n --stdio > {report_path}")
    
    # parse the report
    print("parsing report...")
    CYCLE_KEY = "cpu_atom/instructions:u/"
    INSTR_KEY = "cpu_atom/cycles:u/"
    EVENT_TYPES = {CYCLE_KEY, INSTR_KEY}
    blocks = {}
    cur_block_key = None
    text = open(report_path, 'r').read()
    for line in text.split("\n"):
        if line.startswith("#"):
            if line.startswith("# Samples: "):
                event_type = line.split(' ')[5][1:-1]
                if event_type in EVENT_TYPES:
                    # Start Block
                    cur_block_key = event_type
                    blocks[cur_block_key] = []
        elif line == "":
            # End Block
            cur_block_key = None
        elif cur_block_key is not None:
            event_cnt = int([tok for tok in line.split() if tok != ""][1])*EVENTS_PER_SAMPLE
            symbol = line.split('[.]')[1].strip()
            blocks[cur_block_key].append((event_cnt, symbol))

    instr_counts_per_sym = dict()
    for event_cnt, sym in blocks[INSTR_KEY]:
        instr_counts_per_sym[sym] = event_cnt
    cycle_counts_per_sym = dict()
    for event_cnt, sym in blocks[CYCLE_KEY]:
        cycle_counts_per_sym[sym] = event_cnt

    cmn_syms = set(instr_counts_per_sym.keys())
    for sym in cycle_counts_per_sym:
        cmn_syms.add(sym)

    return [{
        "symbol": sym,
        "cycle_count": cycle_counts_per_sym.get(sym, 0),
        "instr_count": instr_counts_per_sym.get(sym, 0)
    } for sym in cmn_syms]
                


class SymbolsCollector(framework.collections.Collector):
    def get_field_names(self) -> list[str]:
        return [
            "exe_path",
            "thread_count",
            "conf_type"
        ]

    def get_collector(self) -> Callable:
        return _collect_symbols

    def create_config(exe_path: str, thread_count: int) -> Config:
        return Config({
            "conf_type": "symbols",
            "exe_path": exe_path,
            "thread_count": thread_count,
        })

def _collect_symbols(master: JobMaster, config: SymbolsCollector) -> object:
    data_path = f"{config.exe_path}.tmp.data"
    # safesystem(f"numactl -N 0 perf record {exe_path} && mv perf.data {data_path}")
    START_CPU_IDX = 16 # For raptor lake i9-13900, to only use efficiency cores.

    omp_prefix = f"OMP_NUM_THREADS={config.thread_count}"
    numactl_prefix = f"numactl --physcpubind={START_CPU_IDX}-{START_CPU_IDX+config.thread_count-1}"
    perf_prefix = f"perf record -ecycles:u,instructions:u -c {EVENTS_PER_SAMPLE}"
    
    safesystem(f"{omp_prefix} {numactl_prefix} {perf_prefix} {config.exe_path} && mv perf.data {data_path}")
    res = _report_and_parse(config.exe_path, data_path)
    return res