from framework.config import *
import json, os
import random
from typeguard import typechecked

def get_rand_id(value: int | None = None):
    return random.randint(0, 1e12) if value is None else value
    
class Database:
    DEFAULT_BASEPATH = "/root/amdahl-gen/db_storage"

    def __init__(self, basepath: str = None):
        self.basepath = Database.DEFAULT_BASEPATH if basepath is None else basepath

    def provide(self, json_content: object) -> int:
        """returns the ressult id of the newly created object if operation succeded"""
        return self._store_object(json_content)

    def _get_objects(self):
        return (
            obj for obj
            in (self._load_object(fname) for fname in os.listdir(self.basepath))
            if isinstance(obj, dict) and "$id" in obj.keys()
        )

    def query(self, config: Config) -> set[int]:
        results: set[int] = set()
        for obj in self._get_objects():
            if "config" not in obj.keys():
                continue
            try:
                if config == Config(obj["config"]):
                    results.add(int(obj["$id"]))
            except InvalidConfig as e:
                print(f"warning: bad config at \"{self.basepath}/{obj['$id']}\": {e}", file=sys.stderr)
                continue
        return results

    def get(self, elem_id: int) -> object | None:
        for obj in self._get_objects():
            if int(obj["$id"]) == elem_id:
                return obj
        return None


    def _open_id(self, elem_id, mode):
        return open(f"{self.basepath}/{elem_id}.json", mode)

    def _store_object(self, obj: object) -> int:
        elem_id = get_rand_id()
        obj["$id"] = elem_id
        with self._open_id(elem_id, 'w') as f:
            json.dump(obj, f, indent=4)
        return elem_id
        
    def _load_object(self, fname: str) -> dict:
        with self._open_id(fname.removesuffix('.json'), 'r') as f:
            return json.load(f)
        