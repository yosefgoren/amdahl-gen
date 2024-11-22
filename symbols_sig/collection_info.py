from framework.config import *
from framework.job_master import *
import framework.collector
from symbols.collection_info import SymbolsCollector
from common.operators import *
from typing import Callable
from typeguard import typechecked
from common.operators import map_bysym

@typechecked
def _average(s: list) -> float | None:
    if len(s) == 0:
        return None
    return sum(s)/len(s)


class SymbolsSigCollector(framework.collector.Collector):
    def get_field_names(self) -> list[str]:
        return [
            "exe_path",
            "thread_count",
            "num_reps",
            "conf_type"
        ]

    def get_collector(self) -> Callable:
        return collect_symbols_sig

    def create_config(exe_path: str, thread_count: int, num_reps: int) -> Config:
        return Config({
            "conf_type": "symbols_sig",
            "exe_path": exe_path,
            "thread_count": thread_count,
            "num_reps": num_reps,
        })
    
def collect_symbols_sig(master: JobMaster, config: SymbolsSigCollector) -> list[object]:
    if any(not hasattr(config, attr) for attr in ["exe_path", "thread_count", "num_reps"]):
        raise InvalidConfig(config)
    conf: Config = SymbolsCollector.create_config(config.exe_path, config.thread_count)
    result_ids: set[int] = master.satisfy(conf, config.num_reps)
    results = [master.db.get(res_id) for res_id in result_ids]
    entries_bysym: dict[int, list[object]] = map_bysym(results)
    MIN_ALLOWED_IPC = 0.000001 # This is to avoid crashing due to division by IPC later. Results with 0 IPC are likely noisy anyways
    return list(filter(lambda d: d["avg_ipc"] is not None and d["avg_ipc"] > MIN_ALLOWED_IPC, [{
        "symbol": sym,
        "avg_ipc": _average([entry["instr_count"]/entry["cycle_count"] for entry in entries if entry["cycle_count"] > 0])
    } for sym, entries in entries_bysym.items()]))