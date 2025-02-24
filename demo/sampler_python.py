import time
import ctypes

from eacgm.bpf import BccBPF
from eacgm.sampler import eBPFSampler

text = """
#include <uapi/linux/ptrace.h>

int PyObject_CallFunctionEntry(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    bpf_trace_printk("%ld start PyObject_CallFunction\\n", ts);
    return 0;
};

int PyObject_CallFunctionExit(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    bpf_trace_printk("%ld end PyObject_CallFunction\\n", ts);
    return 0;
};
"""

bpf = BccBPF("PythoneBPF", text, ["-w"])

attach_config = [
    {
        "name": "PythonSampler",
        "exe_path": [
            "/home/txx/data/miniconda3/envs/py312-torch24-cu124/bin/python",
        ],
        "exe_sym": [
            "PyObject_CallFunction",
        ]
    },
]

sampler = eBPFSampler(bpf)

sampler.run(attach_config)

while True:
    try:
        samples = sampler.sample(time_stamp=1)
        for sample in samples:
            print(sample)
        print("---")
    except KeyboardInterrupt:
        break

sampler.close()