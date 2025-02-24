import time
import json

from eacgm.sampler import NVMLSampler

sampler = NVMLSampler()

sampler.run()

states = []
while True:
    try:
        for sample in sampler.sample(time_stamp=1):
            # print(sample)
            states.append({
                "ts": time.time_ns(),
                "pid": sample.pid,
                "gpu": sample.gpu,
                "gpu_utl": sample.sm,
                "mem": sample.mem,
                "encode_utl": sample.enc,
                "decode_utl": sample.dec,
            })
        time.sleep(2)
        print("---")
    except KeyboardInterrupt:
        break

sampler.close()
json.dump(states, open("nvml.json", "w", encoding="utf-8"), indent=4)