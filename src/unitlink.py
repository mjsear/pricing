import numpy as np
import pandas as pd

prem = 150*np.ones((10,1))
alloc = 0.99 * np.ones((10,1))
alloc[0] = 0.65
bospread = 0.05
prem * alloc * bospread

def d(i):
    return 1-(1+i)**-1