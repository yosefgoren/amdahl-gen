import json, jsonschema
import os, sys
from framework.context import get_context
from framework.collections import Collector
import importlib

# def _load_if_collection_type(type_name: str):
#     """checks if the given collection type name is indeed a collection type and if so _ runs it"""
#     tgt_file = f"{type_name}/collection_info.py"
#     conf_schema_file = f"{type_name}/{type_name}.config.schema.json"
#     result_schema_file = f"{type_name}/{type_name}.result.schema.json"
#     try:
#         if all(os.path.isfile(file) for file in [tgt_file, conf_schema_file, result_schema_file]):
#             module_name = tgt_file.replace('/', '.').removesuffix('.py')
#             return importlib.import_module(module_name)
#     except Exception as e:
#         print(f"error while executing '{tgt_file}':\n\t{e}", file=sys.stderr)
#         exit(1)
#     return None

# def _get_collection_info_class_name(type_name: str) -> str:
#     return f"{type_name[0].upper()}{type_name[1:]}Collector()"

class InvalidConfig(Exception):
    def __init__(self, conf_obj: object):
        self.conf_obj = conf_obj
    
    def __str__(self):
        return f"invalid configuration: '{self.conf_obj}'"

class Config:
    _COLLECTORS = None
    def _get_collectors() -> dict[str, Collector]:
        if Config._COLLECTORS is None:
            # Config._COLLECTORS = {
            #     col_type: eval(_get_collection_info_class_name(col_type))
            #     for col_type in os.listdir("./") if _load_if_collection_type(col_type)
            # }
            # modules = {
            #     col_type: _load_if_collection_type(col_type) for col_type in os.listdir("./")
            # }
            # Config._COLLECTORS = {
            #     col_type: module.ThisCollector
            #     for col_type, module in modules if module is not None
            # }
            
            from sample.collection_info import SampleCollector as sample_col
            from significant.collection_info import SignificantCollector as sig_col
            from alpha.collection_info import AlphaCollector as alpha_col
            Config._COLLECTORS = {
                "sample": sample_col,
                "significant": sig_col,
                "alpha": alpha_col
            }
            
            
        return Config._COLLECTORS

    def __init__(self, json_conf: dict):
        if not isinstance(json_conf, dict) or "conf_type" not in json_conf.keys():
            raise InvalidConfig(json_conf)
        self.my_type = json_conf["conf_type"]
        col_info: Collector = Config._get_collectors()[self.my_type]
        field_names = col_info().get_field_names()
        self._fields = {name: json_conf[name] for name in field_names}
        for key, value in self._fields.items():
            self.__dict__[key] = value
        self._collector = col_info().get_collector()

    def _serialize(self) -> dict:
        return self._fields

    def __eq__(self, other) -> bool:
        for key, value in self._fields.items():
            if key not in other.__dict__.keys() or other.__dict__[key] != value:
                return False
        return True

    def collect(self, master) -> dict:
        json_conf = self._serialize()
        jsonschema.validate(json_conf, json.load(open(f"./{self.my_type}/{self.my_type}.config.schema.json")))
        result = {
            "data": self._collector(master, self),
            "context": get_context(),
            "config": json_conf,
        }
        jsonschema.validate(result, json.load(open(f"./{self.my_type}/{self.my_type}.result.schema.json")))
        return result
