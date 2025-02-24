import os
import time
import json

from eacgm.bpf import BccBPF
from eacgm.sampler import eBPFSampler, NVMLSampler, GPUSampler
from eacgm.collector import to_perfetto

for filename in os.listdir("res"):
    os.remove(os.path.join("res", filename))
start_time = time.time_ns() - time.clock_gettime_ns(time.CLOCK_MONOTONIC)
start_time /= 1_000

torch_func_sym = {
    "TorchAdd": "_ZN5torch8autogradL15THPVariable_addEP7_objectS2_S2_",
    "TorchSub": "_ZN5torch8autogradL15THPVariable_subEP7_objectS2_S2_",
    "TorchMul": "_ZN5torch8autogradL15THPVariable_mulEP7_objectS2_S2_",
    "TorchMatmul": "_ZN5torch8autogradL18THPVariable_matmulEP7_objectS2_S2_",
    "TorchDiv": "_ZN5torch8autogradL15THPVariable_divEP7_objectS2_S2_",
    "TorchLinear": "_ZN5torch8autogradL18THPVariable_linearEP7_objectS2_S2_",
    "TorchConv2d": "_ZN5torch8autogradL18THPVariable_conv2dEP7_objectS2_S2_",
    "TorchReLU": "_ZN5torch8autogradL16THPVariable_reluEP7_objectS2_S2_",
    "TorchSigmoid": "_ZN5torch8autogradL19THPVariable_sigmoidEP7_objectS2_S2_",
    "TorchTanh": "_ZN5torch8autogradL16THPVariable_tanhEP7_objectS2_S2_",
    "TorchSoftmax": "_ZN5torch8autogradL19THPVariable_softmaxEP7_objectS2_S2_",
    "TorchMSELoss": "_ZN5torch8autogradL20THPVariable_mse_lossEP7_objectS2_S2_",
    "TorchBCELoss": "_ZN5torch8autogradL32THPVariable_binary_cross_entropyEP7_objectS2_S2_",
    "TorchCrossEntropyLoss": "_ZN5torch8autogradL30THPVariable_cross_entropy_lossEP7_objectS2_S2_",
    "TorchConvTranspose2d": "_ZN5torch8autogradL28THPVariable_conv_transpose2dEP7_objectS2_S2_",
    "TorchMaxUnpool2d": "_ZN5torch8autogradL24THPVariable_max_unpool2dEP7_objectS2_S2_",
    "TorchBatchNorm2d": "_ZN5torch8autogradL22THPVariable_batch_normEP7_objectS2_S2_",
    "TorchAvgPool2d": "_ZN5torch8autogradL22THPVariable_avg_pool2dEP7_objectS2_S2_",
    "TorchMaxPool2d": "_ZN5torch8autogradL22THPVariable_max_pool2dEP7_objectS2_S2_",
    "TorchDropout": "_ZN5torch8autogradL19THPVariable_dropoutEP7_objectS2_S2_",
    "TorchEmbedding": "_ZN5torch8autogradL21THPVariable_embeddingEP7_objectS2_S2_",
    "TorchLSTM": "_ZN5torch8autogradL16THPVariable_lstmEP7_objectS2_S2_",
    "TorchAdaptiveMaxPool2d": "_ZN5torch8autogradL31THPVariable_adaptive_max_pool2dEP7_objectS2_S2_",
    "TorchAdaptiveAvgPool2d": "_ZN5torch8autogradL31THPVariable_adaptive_avg_pool2dEP7_objectS2_S2_",
}

torch_template = """
int <TorchSym>Entry(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    bpf_trace_printk("%ld@start@<TorchFunc>\\n", ts);
    return 0;
};

int <TorchSym>Exit(struct pt_regs *ctx){
    u64 ts = bpf_ktime_get_ns();
    bpf_trace_printk("%ld@end@<TorchFunc>\\n", ts);
    return 0;
};
"""

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

for func in torch_func_sym:
    sym = torch_func_sym[func]
    text += torch_template.replace("<TorchSym>", sym).replace("<TorchFunc>", func)

bpf = BccBPF("eACGSampler", text, ["-w"])

attach_config = [
    {
        "name": "CUDASampler",
        "exe_path": [
            "/home/txx/data/miniconda3/envs/eACGM/lib/python3.12/site-packages/nvidia/cuda_runtime/lib/libcudart.so.12",
        ],
        "exe_sym": [
            "cudaLaunchKernel",
        ]
    },
    {
        "name": "NCCLSampler",
        "exe_path": [
            "/home/txx/data/miniconda3/envs/eACGM/lib/python3.12/site-packages/nvidia/nccl/lib/libnccl.so.2",
        ],
        "exe_sym": [
            "ncclAllReduce",
        ]
    },
    {
        "name": "PythonSampler",
        "exe_path": [
            "/home/txx/data/miniconda3/envs/eACGM/bin/python",
        ],
        "exe_sym": [
            # "PyObject_CallFunction",
        ]
    },
    {
        "name": "TorchSampler",
        "exe_path": [
            "/home/txx/data/miniconda3/envs/eACGM/lib/python3.12/site-packages/torch/lib/libtorch_python.so",
        ],
        "exe_sym": [
            torch_func_sym[func] for func in torch_func_sym
        ]
    },
]

eacg_sampler = eBPFSampler(bpf)
nvml_sampler = NVMLSampler()
gpu_sampler  = GPUSampler()

eacg_sampler.run(attach_config)

states = []
while True:
    try:
        samples = []
        samples += eacg_sampler.sample(time_stamp=1)
        samples += nvml_sampler.sample(time_stamp=1)
        samples += gpu_sampler.sample()
        states += samples
        for sample in samples:
            print(sample)
        print("---")
    except KeyboardInterrupt:
        break

eacg_sampler.close()
nvml_sampler.close()
gpu_sampler.close()

ebpf_collector = to_perfetto(states)
json.dump(ebpf_collector, open("res/ebpf.json", "w", encoding="utf-8"), indent=4)
eacg_collector = ebpf_collector
for python_log in os.listdir("res"):
    if "python" not in python_log:
        continue
    python_collector = json.load(open(os.path.join("res", python_log), "r", encoding="utf-8"))
    eacg_collector += python_collector
json.dump(eacg_collector, open("res/eacg.json", "w", encoding="utf-8"), indent=4)