import json, os
from framework.config import *
import random

class ElementId:
    def __init__(self, value: int | None = None):
        self.value = random.randint(0, 1e12) if value is None else value
    
class Database:
    DEFAULT_BASEPATH = "/root/amdahl-gen/db_storage"

    def __init__(self, basepath: str = None):
        self.basepath = Database.DEFAULT_BASEPATH if basepath is None else basepath

    def provide(self, json_content: object) -> ElementId:
        """returns the ressult id of the newly created object if operation succeded"""
        return self._store_object(json_content)

    def _get_objects(self):
        return (
            obj for obj
            in (self._load_object(fname) for fname in os.listdir(self.basepath))
            if isinstance(obj, dict) and "$id" in obj.keys()
        )

    def query(self, config: Config) -> set[ElementId]:
        results: set[ElementId] = set()
        for obj in self._get_objects():
            if "config" not in obj.keys():
                continue
            if config == Config(obj["config"]):
                results.add(ElementId(obj["$id"]))
        return results

    def get(self, elem_id: ElementId) -> object | None:
        for obj in self._get_objects():
            if ElementId(obj["$id"]) == elem_id:
                return obj
        return None


    def _open_id(self, elem_id, mode):
        return open(f"{self.basepath}/{elem_id}", mode)

    def _store_object(self, obj: object) -> ElementId:
        elem_id = ElementId()
        obj["$id"] = elem_id
        with self._open_id(elem_id, 'w') as f:
            json.dump(obj, f)
        return elem_id
        
    def _load_object(self, fname: str) -> dict:
        with self._open_id(fname, 'r') as f:
            return json.load(f)
        