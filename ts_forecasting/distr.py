import numpy as np
import pandas as pd


def _pert(a, b, c, size=1, lamb=4):
    if b <= a:
        raise ValueError('Wrong params for PERT distribution: must be b > a')
    if c <= b:
        raise ValueError('Wrong params for PERT distribution: must be c > b')

    r = c - a
    alpha = 1 + lamb * (b - a) / r
    beta = 1 + lamb * (c - b) / r
    return a + np.random.beta(alpha, beta, size=size) * r


DISTRIBUTIONS = {
    'pert': _pert
}


def generate(name, size, **params):
    fn = DISTRIBUTIONS[name]
    return pd.DataFrame(fn(size=size, **params), columns=['value'])
