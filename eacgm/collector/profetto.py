from typing import List

from eacgm.sampler import eBPFSamplerState

def to_perfetto(states:List[eBPFSamplerState]) -> List:
    res = []
    last_event = {}
    for state in states:
        if not isinstance(state, eBPFSamplerState):
            continue
        state = state.collect()
        name = f"{state['name']}-{state['pid']}"
        last_state = last_event.get(name, None)
        if last_state is None:
            last_event[name] = state
            continue
        if last_state["ph"] == "B" and state["ph"] == "E":
            res.append(last_state)
            res.append(state)
        last_event[name] = state
    return res