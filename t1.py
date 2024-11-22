#!/home/yogo/env/bin/python
from framework.job_master import *
from symbols.collection_info import SymbolsCollector as sym_c
from symbols_sig.collection_info import SymbolsSigCollector as sym_sc
from symbols_alpha.collection_info import SymbolsAlphaCollector as sym_ac
from get_func_body import *
import os
from sys import argv


if len(argv) < 2:
    cmd = input(
    """options for prior results:
        <s>: skip deletion
        <D>: delete them
        <Ctrl+C / Enter>: cancel
    """)
else:
    cmd = argv[1]

if cmd.startswith('D'):
    print("cleaning database")
    os.system("rm -f db_storage/*")
    os.system("rm -f graphs/*")
elif not cmd.startswith('s'):
    print("exiting")
    exit()


m = JobMaster()
thread_counts = [1, 2, 4, 8, 16]
num_reps = 5
exenames = [
    # "./test-targets/fib-static-gcc",
    # "./test-targets/fib-static-clang",
    # "./test-targets/fib-dynamic-clang",
    # "./test-targets/bt.B",
    # "./test-targets/fib-dynamic-gcc",
    # "./test-targets/bt.S",
    "./test-targets/bt.A",
    # "./test-targets/cont",
]

def getfirst(col):
    for elem in col:
        return elem

for name in exenames:
    # m.satisfy(sym_c.create_config(name, thread_counts[0]))
    # m.satisfy(sym_sc.create_config(name, thread_counts[0], num_reps))
    collection_ids = m.satisfy(sym_ac.create_config(name, thread_counts, num_reps))


def get_chat(func, perf):
    return [
        {
            "content": "You are a program scalability estimator agent. Your goal is to predict as accurately as possible how well the performance of the OpenMP C++ code scale as the number of threads running it increases.",
            "role": "system"
        },
        {
            "content": f"In the scale of 'Poorly/Reasonably/Well', how well does the function: '{func}' scale as the number of threads increases?",
            "role": "user"
        },
        {
            "content": f"{perf}",
            "role": "assistant"
        }
    ]



colid = getfirst(collection_ids)
results = m.db.get(colid)["data"]

def get_perf_name(perf: float)->str:
    if perf < 0.02:
        return "Poorly"
    if perf < 0.1:
        return "Resonably"
    return "Well"

print(json.dumps(results, indent=4))
with_src = [
    (get_func_body(res["symbol"].split('(')[0], '/home/yogo/Desktop/NPB-CPP/NPB-OMP/BT/bt.cpp'), get_perf_name(res["alpha"]))
    for res in results
]

dataset = [get_chat(body, perf) for body, perf in with_src if body is not None]

outfile = f'./dataset/{colid}.json'

json.dump(dataset,  open(outfile, 'w'), indent=4)
print(f"results in '{outfile}'.")