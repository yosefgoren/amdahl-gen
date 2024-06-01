from framework.job_master import *
# from sample.collection_info import SampleCollector as si
# from significant.collection_info import SignificantCollector as sc
from alpha.collection_info import AlphaCollector as ac
import os

os.system("rm -f db_storage/*")

m = JobMaster()
thread_counts = [1, 2, 4]
num_reps = 3
exenames = [
    # "./test-targets/fib-static-gcc",
    # "./test-targets/fib-static-clang",
    # "./test-targets/fib-dynamic-clang",
    # "./test-targets/bt.B",
    # "./test-targets/fib-dynamic-gcc",
    "./test-targets/bt.S",
]
for name in exenames:
    m.satisfy(ac.create_config(name, thread_counts, num_reps))
