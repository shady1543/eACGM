# eACGM

**eACGM:** an **e**BPF-based **A**utomated **C**omprehensive **G**overnance and **M**onitoring framework.

[English](README.md) | 中文

- 实现硬件（GPU, NCCL）和软件（CUDA, Python, PyTorch）的全栈追踪；
- 零侵入，低开销；

![img](asset/arch.png)

目前实现了以下功能：

- [x] 基于 eBPF 实现对 CUDA Runtime 的事件探测
- [x] 基于 eBPF 实现对 NCCL GPU 通信库的事件探测
- [x] 基于 eBPF 实现对 Python 虚拟机的函数调用探测
- [x] 基于 eBPF 实现对 Pytorch 的算子探测
- [x] 基于 `libnvml` 实现对进程级的 GPU 信息探测
- [x] 基于 `libnvml` 实现对 GPU 的信息探测
- [x] 实现 eBPF 程序代码自动生成
- [x] 实现对捕获到的 CUDA Runtime 事件进行分析
- [x] 实现对捕获到的 NCCL GPU 通信库事件进行分析
- [x] 实现对捕获到的 Python 虚拟机的函数调用进行分析
- [x] 实现对捕获到的 Pytorch 的算子进行分析

## 可视化

使用 Docker 部署 Grafana 和 MySQL 应用，通过 http://127.0.0.1:3000 访问可视化界面

```bash
cd grafana/
sh ./launch.sh
```

使用 `service.sh` 启动监听服务

```bash
sh ./service.sh
```

使用 `stop.sh` 关闭监听服务

```bash
sh ./stop.sh
```

## 案例演示

`demo` 文件夹下有演示程序：

- `pytorch_example.py`: 一个用于演示的多机多卡 Pytorch 程序
- `sampler_cuda.py`: 使用 eBPF 追踪 CUDA 事件的案例
- `sampler_nccl.py`: 使用 eBPF 追踪 NCCL 事件的案例
- `sampler_torch.py`: 使用 eBPF 追踪 Torch 算子的案例
- `sampler_python.py`: 使用 eBPF 追踪 Python 虚拟机的案例
- `sampler_gpu.py`: 使用 `libnvml` 实现对 GPU 的信息探测
- `sampler_nccl.py`: 使用 `libnvml` 实现对进程级的 GPU 信息探测
- `sampler_eacg.py`: 实现对上述所有信息探测
- `webui.py`: 自动将探测到的数据在 Grafana 上可视化