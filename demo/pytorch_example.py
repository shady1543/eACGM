import os
import time
import json
import torch
import torch.nn as nn
from torch.nn import functional as F
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from tqdm import tqdm

pid = None
sample = []

def init_process(rank, world_size):
    global sample
    dist.init_process_group("nccl", rank=rank, world_size=world_size)

    import sys
    import time

    # [
    #     {
    #         "name": "TorchEmbedding",
    #         "cat": "torch",
    #         "pid": 6274,
    #         "tid": 6274,
    #         "cpu": 10,
    #         "ts": 3660163635.154,
    #         "ph": "B",
    #         "message": []
    #     },
    #     {
    #         "name": "TorchEmbedding",
    #         "cat": "torch",
    #         "pid": 6274,
    #         "tid": 6274,
    #         "cpu": 10,
    #         "ts": 3660194521.558,
    #         "ph": "E",
    #         "message": []
    #     }
    # ]

    func_fliter = [
        "forward_embedding",
        "forward_layer_normal",
        "forward_linear",
        "forward_relu",
        "forward_dropout",
        "forward_multihead_attention",
    ]
    def print_stack_traces(frame, event, arg):
        f_code = frame.f_code
        if f_code.co_name not in func_fliter:
            return
        temp_time = time.clock_gettime_ns(time.CLOCK_MONOTONIC)
        func_name = f_code.co_name
        ph = None
        if event == "call":
            ph = "B"
        elif event == "return":
            ph = "E"
        if ph is None:
            return
        global pid
        sample.append({
            "name": func_name,
            "cat": "python",
            "pid": pid,
            "tid": pid,
            "ts": temp_time / 1_000,
            "ph": ph,
            "message": [],
        })
        return

    sys.setprofile(print_stack_traces)
    return

def cleanup(rank):
    global sample, pid
    dist.destroy_process_group()
    json.dump(sample, open(f"res/python_{pid}.json", "w", encoding="utf-8"), indent=4)
    return

class GPTBlock(nn.Module):
    def __init__(self, embed_dim, num_heads, dropout=0.1):
        super().__init__()
        self.attention = nn.MultiheadAttention(embed_dim, num_heads, dropout=dropout)
        self.ln1 = nn.LayerNorm(embed_dim)
        self.mlp = nn.Sequential(
            nn.Linear(embed_dim, 4 * embed_dim),
            nn.ReLU(),
            nn.Linear(4 * embed_dim, embed_dim),
            nn.Dropout(dropout),
        )
        self.ln2 = nn.LayerNorm(embed_dim)

    def forward(self, x):
        attn_output, _ = self.attention(x, x, x, need_weights=False)
        x = self.ln1(x + attn_output)  # Residual Connection + Layer Norm
        x = self.ln2(x + self.mlp(x))  # Residual Connection + Layer Norm
        return x

class GPT2(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_heads, num_layers, max_len, dropout=0.1):
        super().__init__()
        self.token_embedding = nn.Embedding(vocab_size, embed_dim)
        self.position_embedding = nn.Embedding(max_len, embed_dim)
        self.blocks = nn.ModuleList(
            [GPTBlock(embed_dim, num_heads, dropout) for _ in range(num_layers)]
        )
        self.ln = nn.LayerNorm(embed_dim)
        self.head = nn.Linear(embed_dim, vocab_size, bias=False)
        return

    def forward(self, x):
        b, t = x.size()
        assert t <= self.position_embedding.num_embeddings, "Sequence length exceeds model capacity!"

        token_embeds = self.token_embedding(x)  # Token Embeddings
        position_ids = torch.arange(t, device=x.device).unsqueeze(0).expand(b, t)
        position_embeds = self.position_embedding(position_ids)  # Positional Embeddings

        x = token_embeds + position_embeds

        for block in self.blocks:
            x = block(x)

        x = self.ln(x)
        logits = self.head(x)
        return logits

def work(model, epochs, sleep, device):

    vocab_size = 50257
    embed_dim = 768
    num_heads = 12
    num_layers = 12
    max_len = 1024
    dropout = 0.1

    dummy_input = torch.randint(0, vocab_size, (4, max_len)).to(device)
    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)

    for _ in tqdm(range(epochs)):
        # with torch.no_grad():
        logits = model(dummy_input)
        label  = torch.randn_like(logits).to(device)

        optimizer.zero_grad()
        loss = criterion(logits, label)
        loss.backward()
        optimizer.step()

        time.sleep(sleep)
    return

def main(rank, world_size):
    global pid
    pid = os.getpid()
    init_process(rank, world_size)
    
    device = f"cuda:{rank}"
    # device = f"cuda:1"
    torch.cuda.set_device(rank)

    vocab_size = 50257
    embed_dim = 768
    num_heads = 12
    num_layers = 12
    max_len = 1024
    dropout = 0.1

    model = GPT2(vocab_size, embed_dim, num_heads, num_layers, max_len, dropout).to(device)
    model = DDP(model, device_ids=[rank])

    epochs = 1
    sleep = 0.0

    work(model, epochs, sleep, device)

    cleanup(rank)

if __name__ == "__main__":
    world_size = 6
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '10001'
    torch.multiprocessing.spawn(main, args=(world_size,), nprocs=world_size, join=True)
