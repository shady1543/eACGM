import time
import json

from eacgm.bpf import BccBPF
from eacgm.sampler import eBPFSampler
from eacgm.collector import to_perfetto

func_sym = {
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

template = """
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

text = ""
for func in func_sym:
    sym = func_sym[func]
    text += template.replace("<TorchSym>", sym).replace("<TorchFunc>", func)

bpf = BccBPF("TorcheBPF", text, ["-w"])

attach_config = [
    {
        "name": "TorchSampler",
        "exe_path": [
            "/home/txx/data/miniconda3/envs/eACGM/lib/python3.12/site-packages/torch/./lib/libtorch_python.so",
        ],
        "exe_sym": [
            "_ZN5torch8autogradL15THPVariable_addEP7_objectS2_S2_",
            "_ZN5torch8autogradL15THPVariable_subEP7_objectS2_S2_",
            "_ZN5torch8autogradL15THPVariable_mulEP7_objectS2_S2_",
            "_ZN5torch8autogradL18THPVariable_matmulEP7_objectS2_S2_",
            "_ZN5torch8autogradL15THPVariable_divEP7_objectS2_S2_",
            "_ZN5torch8autogradL18THPVariable_linearEP7_objectS2_S2_",
            "_ZN5torch8autogradL18THPVariable_conv2dEP7_objectS2_S2_",
            "_ZN5torch8autogradL16THPVariable_reluEP7_objectS2_S2_",
            "_ZN5torch8autogradL19THPVariable_sigmoidEP7_objectS2_S2_",
            "_ZN5torch8autogradL16THPVariable_tanhEP7_objectS2_S2_",
            "_ZN5torch8autogradL19THPVariable_softmaxEP7_objectS2_S2_",
            "_ZN5torch8autogradL20THPVariable_mse_lossEP7_objectS2_S2_",
            "_ZN5torch8autogradL32THPVariable_binary_cross_entropyEP7_objectS2_S2_",
            "_ZN5torch8autogradL30THPVariable_cross_entropy_lossEP7_objectS2_S2_",
            "_ZN5torch8autogradL28THPVariable_conv_transpose2dEP7_objectS2_S2_",
            "_ZN5torch8autogradL24THPVariable_max_unpool2dEP7_objectS2_S2_",
            "_ZN5torch8autogradL22THPVariable_batch_normEP7_objectS2_S2_",
            "_ZN5torch8autogradL22THPVariable_avg_pool2dEP7_objectS2_S2_",
            "_ZN5torch8autogradL22THPVariable_max_pool2dEP7_objectS2_S2_",
            "_ZN5torch8autogradL19THPVariable_dropoutEP7_objectS2_S2_",
            "_ZN5torch8autogradL21THPVariable_embeddingEP7_objectS2_S2_",
            "_ZN5torch8autogradL16THPVariable_lstmEP7_objectS2_S2_",
            "_ZN5torch8autogradL31THPVariable_adaptive_max_pool2dEP7_objectS2_S2_",
            "_ZN5torch8autogradL31THPVariable_adaptive_avg_pool2dEP7_objectS2_S2_",
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
json.dump(collector, open("torch.json", "w", encoding="utf-8"), indent=4)