import time
import json

from eacgm.sampler import GPUSampler

sampler = GPUSampler()

sampler.run()

states = []
while True:
    try:
        samples = sampler.sample()
        for sample in samples:
            states.append({
                "ts": time.time_ns(),
                "gpu": sample.gpu,
                "gpu_utl": sample.sm,
                "totMem": sample.totMem,
                "usedMem": sample.usedMem,
                "encode_utl": sample.enc,
                "decode_utl": sample.dec,
                "temperature": sample.tmp,
                "fan_utl": sample.fan,
                "usedPower": sample.usedPower,
                "totPower": sample.totPower,
            })
            # print(sample)
        time.sleep(1)
        print("---")
    except KeyboardInterrupt:
        break

sampler.close()
json.dump(states, open("gpu.json", "w", encoding="utf-8"), indent=4)