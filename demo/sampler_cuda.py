import time
import json

from eacgm.bpf import BccBPF
from eacgm.sampler import eBPFSampler
from eacgm.collector import to_perfetto

text = """
// #include <cuda_runtime.h>
#include <uapi/linux/ptrace.h>

struct dim3 {
    unsigned int x, y, z;
};

int cudaMallocEntry(struct pt_regs *ctx){
    u64 malloc_ptr = PT_REGS_PARM1(ctx);
    u64 byte_length = PT_REGS_PARM2(ctx);
    u64 ts = bpf_ktime_get_ns();
    bpf_trace_printk("%ld@start@cudaMalloc@%ld@%ld\\n", ts, malloc_ptr, byte_length);
    return 0;
};

int cudaMallocExit(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    bpf_trace_printk("%ld@end@cudaMalloc\\n", ts);
    return 0;
};

int cudaMemcpyEntry(struct pt_regs *ctx){
    u64 byte_length = PT_REGS_PARM3(ctx);
    u64 memcpy_kind = PT_REGS_PARM4(ctx);
    u64 ts = bpf_ktime_get_ns();
    bpf_trace_printk("%ld@start@cudaMemcpy@%ld@%ld\\n", ts, memcpy_kind);
    return 0;
};

int cudaMemcpyExit(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    bpf_trace_printk("%ld@end@cudaMemcpy\\n", ts);
    return 0;
};

int cudaFreeEntry(struct pt_regs *ctx){
    u64 malloc_ptr = PT_REGS_PARM1(ctx);
    u64 ts = bpf_ktime_get_ns();
    bpf_trace_printk("%ld@start@cudaFree@%ld\\n", malloc_ptr, ts);
    return 0;
};

int cudaFreeExit(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    bpf_trace_printk("%ld@end@cudaFree\\n", ts);
    return 0;
};

int cudaLaunchKernelEntry(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    u32 g_x = PT_REGS_PARM2(ctx) & 0xFFFF;
    u32 g_y = PT_REGS_PARM2(ctx) >> 32;
    u32 g_z = PT_REGS_PARM3(ctx) & 0xFFFF;
    u32 b_x = PT_REGS_PARM4(ctx) & 0xFFFF;
    u32 b_y = PT_REGS_PARM4(ctx) >> 32;
    u32 b_z = PT_REGS_PARM5(ctx) & 0xFFFF;
    // bpf_trace_printk("0 ----- cudaLaunchKernel %u %u %u\\n", g_x, g_y, g_z);
    // bpf_trace_printk("0 ----- cudaLaunchKernel %u %u %u\\n", b_x, b_y, b_z);
    u32 stream_num = g_x * g_y * g_z * b_x * b_y * b_z;
    bpf_trace_printk("%ld@start@cudaLaunchKernel@%u\\n", ts, stream_num);
    return 0;
};

int cudaLaunchKernelExit(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    bpf_trace_printk("%ld@end@cudaLaunchKernel\\n", ts);
    return 0;
};
"""

bpf = BccBPF("CUDAeBPF", text, ["-w"])

attach_config = [
    {
        "name": "CUDASampler",
        "exe_path": [
            "/home/txx/data/miniconda3/envs/eACGM/lib/python3.12/site-packages/nvidia/cuda_runtime/lib/libcudart.so.12",
        ],
        "exe_sym": [
            "cudaMalloc",
            "cudaMemcpy",
            "cudaFree",
            "cudaLaunchKernel",
        ]
    },
]

sampler = eBPFSampler(bpf)

sampler.run(attach_config)

states = []
while True:
    try:
        samples = sampler.sample(time_stamp=1)
        states += samples
        # for sample in samples:
            # print(sample)
        # print("---")
    except KeyboardInterrupt:
        break

sampler.close()

collector = to_perfetto(states)
json.dump(collector, open("cuda.json", "w", encoding="utf-8"), indent=4)