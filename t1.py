from framework.job_master import *
from symbols.collection_info import SymbolsCollector as sym_c
from symbols_sig.collection_info import SymbolsSigCollector as sym_sc
from symbols_alpha.collection_info import SymbolsAlphaCollector as sym_ac
import os

if not input(
"""options for prior results:
    <Enter>: delete them
    <Ctrl+C>: cancel
    <s>: skip deletion
""").startswith('s'):
    os.system("rm -f db_storage/*")
    os.system("rm -f graphs/*")

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
]
for name in exenames:
    # m.satisfy(sym_c.create_config(name, thread_counts[0]))
    # m.satisfy(sym_sc.create_config(name, thread_counts[0], num_reps))
    m.satisfy(sym_ac.create_config(name, thread_counts, num_reps))