from context import get_context
import json, jsonschema
import os
from framework.collections import CollectionInfo

def _load_if_collection_type(type_name: str) -> bool:
    """checks if the given collection type name is indeed a collection type and if so - runs it"""
    tgt_file = f"{type_name}/collection_info.py"
    conf_schema_file = f"{type_name}/{type_name}.config.schema.json"
    result_schema_file = f"{type_name}/{type_name}.result.schema.json"
    try:
        if all(os.path.isfile(file) for file in [tgt_file, conf_schema_file, result_schema_file]):
            exec(open(tgt_file, 'r').read())
            return True
    except Exception as e:
        pass
    return False

def _get_collection_info_class_name(type_name: str) -> str:
    return f"{type_name[0].upper()}{type_name[1:]}CollectionInfo()"

class Config:
    _COLLECTION_INFOS: dict[str, CollectionInfo] = {
        col_type: eval(_get_collection_info_class_name(col_type))
        for col_type in os.listdir("./") if _load_if_collection_type(col_type)
    }

    def __init__(self, json_conf: dict):
        col_info: CollectionInfo = Config._COLLECTION_INFOS[self.my_type]
        self.my_type = json_conf["conf_type"]
        field_names = col_info.get_field_names()
        self._fields = {name: json_conf[name] for name in field_names}
        for key, value in self._fields.items():
            self.__dict__[key] = value
        self._collector = col_info.get_collector()

    def _serialize(self) -> dict:
        return self._fields

    def __eq__(self, other) -> bool:
        for key, value in self._fields:
            if other.__dict__[key] != value:
                return False
        return True

    def collect(self):
        json_conf = self._serialize()
        jsonschema.validate(json_conf, json.load(open(f"./{self.my_type}/{self.my_type}.config.schema.json")))
        result = {
            "data": self._collector(self),
            "context": get_context(),
            "config": json_conf
        }
        jsonschema.validate(result, json.load(open(f"./{self.my_type}/{self.my_type}.result.schema.json")))
