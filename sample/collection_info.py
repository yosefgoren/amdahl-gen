from sample.parse_perfanno import *
from framework.collections import CollectionInfo
from framework.config import *
from framework.job_master import *

def perf_exec(exe_path: str) -> str:
    pass

def annotate_and_parse(data_path) -> str:
    pass

def _collect_sample(master: JobMaster, config: object) -> object:
    output_path = perf_exec(config["exe-path"])

    return annotate_and_parse(output_path)


class SampleCollectionInfo(CollectionInfo):
    def get_field_names(self) -> list[str]:
        return [
            "exe_path",
            "thread_count"
        ]

    def get_collector(self) -> function:
        return _collect_sample

    def create_config(exe_path: str, thread_count: int) -> Config:
        return Config({
            "conf_type": "sample",
            "exe_path": exe_path,
            "thread_count": thread_count,
        })