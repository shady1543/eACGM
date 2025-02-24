# eACGM

**eACGM:** an **e**BPF-based **A**utomated **C**omprehensive **G**overnance and **M**onitoring framework.

English | [中文](README_zh.md)

- Full-stack tracing for hardware (GPU, NCCL) and software (CUDA, Python, PyTorch).
- Zero-intrusive & low overhead.

![img](asset/arch.png)

Currently implemented features:

- [x] Event detection for CUDA Runtime based on eBPF
- [x] Event detection for NCCL GPU communication library based on eBPF
- [x] Function call detection for Python virtual machine based on eBPF
- [x] Operator detection for Pytorch based on eBPF
- [x] Process-level GPU information detection based on libnvml
- [x] GPU information detection based on `libnvml`
- [x] Automatic generation of eBPF program code
- [x] Analysis of captured CUDA Runtime events
- [x] Analysis of captured NCCL GPU communication library events
- [x] Analysis of captured Python virtual machine function calls
- [x] Analysis of captured Pytorch operators

## Visualization

Deploy Grafana and MySQL applications using Docker, and access the visualization interface via http://127.0.0.1:3000

```bash
cd grafana/
sh ./launch.sh
```

Use `service.sh` to start the monitoring service

```bash
sh ./service.sh
```

Use `stop.sh` to stop the monitoring service

```bash
sh ./stop.sh
```

## Case Demonstration

The `demo` folder contains demonstration programs:

- `pytorch_example.py`: A multi-machine, multi-GPU Pytorch program for demonstration.
- `sampler_cuda.py`: Example of using eBPF to trace CUDA events.
- `sampler_nccl.py`: Example of using eBPF to trace NCCL events.
- `sampler_torch.py`: Example of using eBPF to trace Torch operators.
- `sampler_python.py`: Example of using eBPF to trace Python virtual machine.
- `sampler_gpu.py`: GPU information detection using `libnvml`.
- `sampler_nccl.py`: Process-level GPU information detection using `libnvml`.
- `sampler_eacg.py`: Detection of all the above information.
- `webui.py`: Automatically visualize the detected data on Grafana.