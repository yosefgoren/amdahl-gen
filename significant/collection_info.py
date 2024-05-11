from framework.collections import CollectionInfo
from framework.config import *
from framework.job_master import *
from sample.collection_info import SampleCollectionInfo
from common.operators import *

def _average(s) -> float:
    return sum(s)/len(s)

def collect_significant(master: JobMaster, config: Config) -> list[object]:
    conf: Config = SampleCollectionInfo.create_config(config.exe_path, config.thread_count)
    result_ids: set[ElementId] = master.satisfy(conf, config.num_reps)
    results = [master.db.get(res_id) for res_id in result_ids]
    entries_byline: dict[int, list[object]] = map_byline(results)
    return [{
        "lineno": lineno,
        "avg_runtime_milisec": _average(entry["times_executed"] for entry in entries)
    } for lineno, entries in entries_byline.items()]

class SignificantCollectionInfo(CollectionInfo):
    def get_field_names(self) -> list[str]:
        return [
            "exe_path",
            "thread_count",
            "num_reps"
        ]

    def get_collector(self) -> function:
        return collect_significant

    def create_config(exe_path: str, thread_counts: list[int], num_reps: int) -> Config:
        return Config({
            "conf_type": "alpha",
            "exe_path": exe_path,
            "thread_counts": thread_counts,
            "num_reps": num_reps,
        })
