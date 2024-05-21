from framework.config import *
from framework.database import *

class JobMaster:
    def __init__(self):
        self.db = Database()

    def satisfy(self, config: Config, amount_required: int = 1, exclude_results: set[int] = set()) -> set[int]:
        """
            ensures that result which satisfy the requirments of 'config' are satisfied,
            either by existing entries in the database, or by collecting new results into the database.
            
            'config': describes the collection requirments.
            'amount_required': the number of results which satisfy the requirements of 'config' are required.
            'exclude_results': id's of results which should be ignored and not be included in results.
        """
        initial_matches: set[int] = self.db.query(config)
        
        valid_matches = initial_matches - exclude_results
        while amount_required > len(valid_matches):
            result = config.collect(self)
            res_id = self.db.provide(result)
            valid_matches.add(res_id)

        return set(list(valid_matches)[:amount_required])
