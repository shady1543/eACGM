import time
import json

from eacgm.bpf import BccBPF
from eacgm.sampler import eBPFSampler
from eacgm.collector import to_perfetto

text = """
#include <uapi/linux/ptrace.h>

int ncclAllReduceEntry(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    u64 size_count = PT_REGS_PARM3(ctx);
    u64 data_type  = PT_REGS_PARM4(ctx);
    u64 reduce_op  = PT_REGS_PARM5(ctx);
    bpf_trace_printk("%ld@start@ncclAllReduce@%ld\\n", ts, size_count * 8);
    return 0;
};

int ncclAllReduceExit(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    bpf_trace_printk("%ld@end@ncclAllReduce\\n", ts);
    return 0;
};

int ncclReduceEntry(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    u64 size_count = PT_REGS_PARM3(ctx);
    u64 data_type  = PT_REGS_PARM4(ctx);
    u64 reduce_op  = PT_REGS_PARM5(ctx);
    bpf_trace_printk("%ld@start@ncclReduce@%ld\\n", ts, size_count * 8);
    return 0;
};

int ncclReduceExit(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    bpf_trace_printk("%ld@end@ncclReduce\\n", ts);
    return 0;
};

int ncclBroadcastEntry(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    u64 size_count = PT_REGS_PARM3(ctx);
    u64 data_type  = PT_REGS_PARM4(ctx);
    u64 root_id  = PT_REGS_PARM5(ctx);
    bpf_trace_printk("%ld@start@ncclBroadcast@%ld\\n", ts, size_count * 8);
    return 0;
};

int ncclBroadcastExit(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    bpf_trace_printk("%ld@end@ncclBroadcast\\n", ts);
    return 0;
};

int ncclAllGatherEntry(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    u64 size_count = PT_REGS_PARM3(ctx);
    u64 data_type  = PT_REGS_PARM4(ctx);
    bpf_trace_printk("%ld@start@ncclAllGather@%ld\\n", ts, size_count * 8);
    return 0;
};

int ncclAllGatherExit(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    bpf_trace_printk("%ld@end@ncclAllGather\\n", ts);
    return 0;
};

int ncclSendEntry(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    u64 size_count = PT_REGS_PARM2(ctx);
    u64 data_type  = PT_REGS_PARM3(ctx);
    bpf_trace_printk("%ld@start@ncclSend@%ld\\n", ts, size_count * 8);
    return 0;
};

int ncclSendExit(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    bpf_trace_printk("%ld@end@ncclSend\\n", ts);
    return 0;
};

int ncclRecvEntry(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    u64 size_count = PT_REGS_PARM2(ctx);
    u64 data_type  = PT_REGS_PARM3(ctx);
    bpf_trace_printk("%ld@start@ncclRecv@%ld\\n", ts, size_count * 8);
    return 0;
};

int ncclRecvExit(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    bpf_trace_printk("%ld@end@ncclRecv\\n", ts);
    return 0;
};
"""

bpf = BccBPF("NCCLeBPF", text, ["-w"])

attach_config = [
    {
        "name": "NCCLSampler",
        "exe_path": [
            "/home/txx/data/miniconda3/envs/eACGM/lib/python3.12/site-packages/nvidia/nccl/lib/libnccl.so.2",
        ],
        "exe_sym": [
            "ncclAllReduce",
            "ncclReduce",
            "ncclBroadcast",
            "ncclAllGather",
            "ncclSend",
            "ncclRecv",
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
        #     print(sample)
        # print("---")
    except KeyboardInterrupt:
        break

sampler.close()
collector = to_perfetto(states)
json.dump(collector, open("nccl.json", "w", encoding="utf-8"), indent=4)