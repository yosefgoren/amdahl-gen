from typeguard import typechecked
from typing import Iterable

@typechecked
def setsum(sets: Iterable[set]) -> set:
    res = set()
    for s in sets:
        res.union(s)
    return res

def map_byline(results: list[dict]) -> dict[int, list]:
    byline_results = [
        {entry["lineno"]: entry for entry in res["data"]}
        for res in results
    ]
    byline_entries = dict()
    all_linenos = setsum(res.keys() for res in byline_results)
    for lineno in all_linenos:
        byline_entries[lineno] = []
        for res in byline_results:
            byline_entries[lineno].append(res[lineno])
        
    return byline_entries