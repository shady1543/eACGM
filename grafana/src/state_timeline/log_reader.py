def reader(path):
    with open(path, 'r') as f:
        data = f.readlines()
    for i, d in enumerate(data):
        data[i] = d.strip().split(' ')
    ret = []
    for d in data:
        tmp = dict()
        tmp['time'] = d[3]
        tmp['op'] = d[5]
        tmp['name'] = d[6]
        ret.append(tmp)
    return ret

def ollama_reader(path):
    with open(path, 'r') as f:
        data = f.readlines()
    for i, d in enumerate(data):
        data[i] = d.strip().split(' ')
    ret = []
    for d in data:
        tmp = dict()
        tmp['time'] = d[0]
        tmp['op'] = "start" if d[2] == "B" else "end"
        tmp['name'] = d[3]
        ret.append(tmp)
    return ret

if __name__ == '__main__':
    data = reader('log/transformer.log')
    print(data)