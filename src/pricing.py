#TO DO NEXT: 
# * Assurance, endowment
# * Modify annuities to allow for deferred onset
# * Fix up all the pandas slices that were previously written assuming unhelpful column names
# * Refactor life function so that 0 means just selected. 


from operator import index
import numpy as np
import pandas as pd
from functools import lru_cache

with open("data/am92rates.csv") as f: #THIS STUFF HAS TO BE CHANGED TO ALLOW FOR MULTIPLE RATES FILES
    rates = pd.read_csv(f, header=0, index_col=0) #THE COLUMN NAMES SHOULD BE UNUSED, EXCEPT IN IN-PROGRESS COMMANDS
    rates.index.name = "Age"
    rates.columns = range(len(rates.columns))

@lru_cache(maxsize=None)
def l(x, sel=rates.columns[-1]):
    """
    Return the *percentage* of lives still living at age x. 
    
    Keyword arguments:
    x   -- Age of the life
    sel -- Remaining years of selection 

    Sel = 0 means ultimate, increasing by one for each year of selection REMAINING.
    Thus, the default sel={number of columns - 1} is a just-selected life [x].

    This should probably be refactored such that sel=0 means select and sel=rates.columns[-1] means 
    ultimate, the current definitions are awkward as hell.
    """
    if x in rates.index:
        if pd.isna(rates.iloc[:,rates.columns[-1] - sel].loc[x]):
            raise IndexError("Age out of select range")
        else:
            if x == rates.index[0] and sel == 0:
                return 1
            lx = l(x-1+sel,0)*(1-rates.iloc[:,-1].loc[x-1+sel]) # (x-1) here is the basic unit, we are using the previous q rate to go back one
            for i in range(1, sel+1):
                lx /= (1-rates.iloc[:,rates.columns[-1]-i].loc[x+sel-i]) # here we are already starting at the destination, so no -1 is needed
            return lx
    else:
        raise IndexError("Age out of table range")

def ann_due(x, sel=rates.columns[-1], interest_rate=0.04, ppy=1):
    """
    Return the expected present value of an lifetime annuity paying amount 1 annually for a life aged x

    Keyword arguments:
    x   -- Age of the life
    sel -- Remaining years of selection 
    interest_rate -- effective annual interest rate
    ppy -- payments per year

    Sel = 0 means ultimate, increasing by one for each year of selection REMAINING.
    Thus, the default sel={number of columns - 1} is a just-selected life [x].
    """
    v = (1+interest_rate)**-1
    adx = sum([v**i * l(i, max(sel-(i-x), 0)) for i in range(x, 121)])/(v**x * l(x, sel))
    
    #pthly adjustment:
    adx = adx - (ppy-1)/(2*ppy)
    return adx

def ann_due_temp(x, duration, sel=rates.columns[-1], interest_rate=0.04, ppy=1):
    """
    Return the expected present value for a limited term annuity paying 1 annually, contingent on life.

    Extends the whole life annuity function to a limited term. Calculated by subtracting a discounted
    whole life annuity at age (x+n) from a whole life annuity at age x.
    """
    
    #adxn = ad(x) - [D(x+n)/D(x)]ad(x+n)
    if duration < rates.columns[-1]:
        print("This number is definitly not correct, durations shorter than select periods are fucked")
    v = (1+interest_rate)**-1
    adx = ann_due(x, sel = sel)
    dx = v**x * l(x, sel)
    dxpn = v**(x+duration) * l(x+duration, 0)
    adxpn = ann_due(x + duration, 0)

    adxn = adx - (dxpn/dx)*adxpn

    #pthly adjustment:
    adxn = adxn - ((ppy - 1)/(2*ppy)) * (1 - v**duration * l(x + duration, 0) / l(x, sel))
    return adxn

def assurance(x, duration = -1, sel=rates.columns[-1], interest_rate=0.04):
    v = (1 + interest_rate)**-1
    base = l(x, sel) * v**x
    ass = sum([l(i, max(sel-(i-x), 0)) * rates.loc[i, min(sel, i-x)] * v**(i+1)/base for i in range(x,121)])
    #max(sel-(i-x), 0) yields 2, 1, 0, 0, 0... for sel = 2
    #min(sel, i-x) yields 0, 1, 2, 2, 2... for sel = 2
    return ass

def endowment(x, duration, sel=rates.columns[-1], interest_rate=0.04):
    v = (1+interest_rate)^-1
    mortality = l(x+duration, 0)/l(x, sel)
    return v^duration * mortality

def endo_ass():
    return assurance() + endowment()

def test():    
    print(f"l_[53]....... = {l(53):.6f}") #0.962110
    print(f"l_53......... = {l(53, sel = 0):.6f}") #0.963005
    print(f":a_[53]...... = {ann_due(53):.6f}") #16.537994
    print(f":a_53........ = {ann_due(53, sel = 0):.6f}") #16.523642
    print(f":a^(4)_53.... = {ann_due(53, sel = 0, ppy = 4):.6f}") #16.148642
    print(f":a_[53]:12... = {ann_due_temp(x = 53, duration = 12):.6f}") #9.508095
    print(f":a_53:12..... = {ann_due_temp(x = 53, duration = 12, sel = 0):.6f}") #9.500278
    print(f":a^(4)_53:12. = {ann_due_temp(x = 53, duration = 12, sel = 0, ppy = 4):.6f}") #9.339830
    print(f"A_[53]....... = {assurance(53):.6f}") #0.363923
    print(f"A_53......... = {assurance(53, sel = 0):.6f}")