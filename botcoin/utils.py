import numpy as np

def optimize(*args):
    args = [np.arange(a[0],a[1],a[2]) for a in args]
    results = []
    for i in args[0]:
        for j in args[1]:
            results.append([i,j])

    return results