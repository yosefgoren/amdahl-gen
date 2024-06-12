def map_byline(results: list[dict]) -> dict[int, list]:
    byline_results = [
        {entry["lineno"]: entry for entry in res["data"]}
        for res in results
    ]
    byline_entries = dict()
    all_linenos = set().union(*[res.keys() for res in byline_results])
    for lineno in all_linenos:
        byline_entries[lineno] = []
        for res in byline_results:
            byline_entries[lineno].append(res[lineno])
        
    return byline_entries

def map_bysym(results: list[dict]) -> dict[str, list]:
    bysym_results = [
        {entry["symbol"]: entry for entry in res["data"]}
        for res in results
    ]
    bysym_entries = dict()
    all_syms = set()
    if len(bysym_results) > 0:
        all_syms = {
            sym
            for sym in bysym_results[0].keys()
            if all(sym in res.keys() for res in bysym_results)
        }
    else:
        print(f"warning: got empty symbols list!")

    for sym in all_syms:
        bysym_entries[sym] = []
        for res in bysym_results:
            bysym_entries[sym].append(res[sym])
        
    return bysym_entries
