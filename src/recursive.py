#Look into np.vectorize(myfunc)

from operator import index
import numpy as np
import pandas as pd
from functools import lru_cache

with open("data/am92rates.csv") as f: #THIS STUFF HAS TO BE CHANGED TO ALLOW FOR MULTIPLE RATES FILES
    am92_rates = pd.read_csv(f, header=0, index_col=0) #THE COLUMN NAMES SHOULD BE UNUSED, EXCEPT IN IN-PROGRESS COMMANDS
    am92_rates.index.name = "Age"
    am92_rates.columns = reversed(range(len(am92_rates.columns)))
    maxsel = am92_rates.columns[0] #NOTICE: This choice of definition for the column labels is important and useful below.
                                   #        Under this definition, ultimate mortality is NAMED "0", and the years of 
                                   #        remaining selection are NAMED "1", "2", etc.

@lru_cache(maxsize=None)
def l(x, sel=maxsel, rates = am92_rates):
    """
    Return the *percentage* of lives still living at age x. 
    
    Keyword arguments:
    x   -- Age of the life
    sel -- Remaining years of selection 

    Sel = 0 means ultimate, increasing by one for each year of selection REMAINING.
    Thus, the default sel={number of columns - 1} is a just-selected life [x].
    """
    if x in rates.index:
        if pd.isna(rates.loc[x,sel]):
            raise IndexError("Age out of select range")
        else:
            if x == rates.index[0] and sel == 0:
                return 1.
            lx = l(x-1+sel,0)*(1-rates.loc[x-1+sel, 0])
            # For select mortality, we aim to start at the equivalent ultimate, and
            # then work our way back up to select. So, e.g., for l_[19], we want to 
            # start with l_21 = l_20 * q_20 and then the l_20 asks for l_19 and so on, 
            # thus we recurse back to the defined radix l_17 = 1
            for i in range(1, sel+1):
                lx /= (1-rates.loc[x+sel-i, i]) 
                # and then here, since we have obtained lx = l_21, we then divide out the px's back up to l_[19]
                # so l_21 /= (1 - q_[19]+1)*(1 - q_[19])
                # here we take advantage of the convenient column labels we have used, 
                # so that the name of the year with i years of selection remaining is just i.
            return lx
    else:
        raise IndexError("Age out of table range")

def q(x, sel = maxsel, rates = am92_rates):
    return(rates.loc[x, sel])

def annuity(x, sel = maxsel, i_rate = 0.04, rates = am92_rates):
    v = i_rate**-1
    root = l(x, sel = maxsel)
    