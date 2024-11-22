from framework.config import *
from framework.job_master import *
import framework.collector
from srclines.collection_info import SrclinesCollector
from common.operators import *
from typing import Callable
from typeguard import typechecked

@typechecked
def _average(s: list) -> float | None:
    if len(s) == 0:
        return None
    return sum(s)/len(s)


class SrclinesSigCollector(framework.collector.Collector):
    def get_field_names(self) -> list[str]:
        return [
            "exe_path",
            "thread_count",
            "num_reps",
            "conf_type"
        ]

    def get_collector(self) -> Callable:
        return collect_srclinessig

    def create_config(exe_path: str, thread_count: int, num_reps: int) -> Config:
        return Config({
            "conf_type": "srclinessig",
            "exe_path": exe_path,
            "thread_count": thread_count,
            "num_reps": num_reps,
        })

def collect_srclinessig(master: JobMaster, config: SrclinesSigCollector) -> list[object]:
    if any(not hasattr(config, attr) for attr in ["exe_path", "thread_count", "num_reps"]):
        raise InvalidConfig(config)
    conf: Config = SrclinesCollector.create_config(config.exe_path, config.thread_count)
    result_ids: set[int] = master.satisfy(conf, config.num_reps)
    results = [master.db.get(res_id) for res_id in result_ids]
    entries_byline: dict[int, list[object]] = map_byline(results)
    return list(filter(lambda d: d["avg_ipc"] is not None, [{
        "lineno": lineno,
        "avg_ipc": _average([entry["instr_count"]/entry["cycle_count"] for entry in entries if entry["cycle_count"] > 0]),
        "linetxt": entries[0]["linetxt"]
    } for lineno, entries in entries_byline.items()]))