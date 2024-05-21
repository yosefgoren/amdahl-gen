from framework.config import *
from framework.job_master import *
import framework.collections
from sample.collection_info import SampleCollector
from common.operators import *
from typing import Callable

def _average(s) -> float:
    return sum(s)/len(s)


class SignificantCollector(framework.collections.Collector):
    def get_field_names(self) -> list[str]:
        return [
            "exe_path",
            "thread_count",
            "num_reps",
            "conf_type"
        ]

    def get_collector(self) -> Callable:
        return collect_significant

    def create_config(exe_path: str, thread_count: int, num_reps: int) -> Config:
        return Config({
            "conf_type": "significant",
            "exe_path": exe_path,
            "thread_count": thread_count,
            "num_reps": num_reps,
        })

def collect_significant(master: JobMaster, config: SignificantCollector) -> list[object]:
    if any(not hasattr(config, attr) for attr in ["exe_path", "thread_count", "num_reps"]):
        raise InvalidConfig(config)
    conf: Config = SampleCollector.create_config(config.exe_path, config.thread_count)
    result_ids: set[int] = master.satisfy(conf, config.num_reps)
    results = [master.db.get(res_id) for res_id in result_ids]
    entries_byline: dict[int, list[object]] = map_byline(results)
    return [{
        "lineno": lineno,
        "avg_runtime_milisec": _average(entry["times_executed"] for entry in entries)
    } for lineno, entries in entries_byline.items()]