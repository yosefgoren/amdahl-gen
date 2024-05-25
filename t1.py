#!/usr/bin/python3

from framework.job_master import *
from sample.collection_info import SampleCollector as si
from significant.collection_info import SignificantCollector as sc
import os

os.system("rm -f db_storage/*")

m = JobMaster()
num_threads = 1
num_reps = 2
exenames = [
    # "./test-targets/fib-static-gcc",
    "./test-targets/fib-dynamic-gcc",
    # "./test-targets/fib-static-clang",
    # "./test-targets/fib-dynamic-clang",
]
for name in exenames:
    m.satisfy(sc.create_config(name, num_threads, num_reps))
