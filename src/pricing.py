#TO DO: 
# * Modify annuities to allow for deferred onset
# * Fix up all the pandas slices that were previously written assuming unhelpful column names

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
                return 1
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

def ann_due(x, sel=maxsel, interest_rate=0.04, ppy=1, rates = am92_rates):
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

def ann_due_temp(x, duration, sel=maxsel, interest_rate=0.04, ppy=1, rates = am92_rates):
    """
    Return the expected present value for a limited term annuity paying 1 annually, contingent on life.

    Extends the whole life annuity function to a limited term. Calculated by subtracting a discounted
    whole life annuity at age (x+n) from a whole life annuity at age x.

    Keyword arguments:
    x -- Age of the life
    duration -- Length of the annuity from x
    sel -- Remaining years of selection; 0 for ultimate mortality
    interest_rate -- effective annual interest rate
    ppy -- payments per year
    rates -- choice of death table

    Sel = 0 means ultimate, increasing by one for each year of selection REMAINING.
    Thus, the default sel={number of columns - 1} is a just-selected life [x].
    """
    
    #adxn = ad(x) - [D(x+n)/D(x)]ad(x+n)
    if duration < maxsel:
        print("This number is definitly not correct, durations shorter than select periods are fucked")
    v = (1+interest_rate)**-1
    adx = ann_due(x, sel = sel, interest_rate=interest_rate)
    dx = v**x * l(x, sel)
    dxpn = v**(x+duration) * l(x+duration, 0)
    adxpn = ann_due(x + duration, 0, interest_rate=interest_rate)

    adxn = adx - (dxpn/dx)*adxpn

    #pthly adjustment:
    adxn = adxn - ((ppy - 1)/(2*ppy)) * (1 - v**duration * l(x + duration, 0) / l(x, sel))
    return adxn

def assurance(x, duration = 0, sel=maxsel, interest_rate=0.04, contn = False, rates = am92_rates):
    """
    Return the expected present value for a limited term annuity paying 1 annually, contingent on life.

    Extends the whole life annuity function to a limited term. Calculated by subtracting a discounted
    whole life annuity at age (x+n) from a whole life annuity at age x.

    Keyword arguments:
    x -- Age of the life
    duration -- Length of the annuity from x
    sel -- Remaining years of selection; 0 for ultimate mortality
    interest_rate -- effective annual interest rate
    contn -- Payment immediately upon death (T) or at EOYOD (F)
    rates -- Choice of death table (AM92, ELT15, PMA)

    Sel = 0 means ultimate, increasing by one for each year of selection REMAINING.
    Thus, the default sel={number of columns - 1} is a just-selected life [x].
    """
    v = (1 + interest_rate)**-1
    base = l(x, sel) * v**x
    terminus = x + duration if duration else rates.index[-1]+1
    ass = sum([l(i, max(sel-(i-x), 0)) * rates.loc[i, max(sel-(i-x), 0)] * v**(i+1)/base for i in range(x, terminus)])
    #max(sel-(i-x), 0) yields 2, 1, 0, 0, 0... for sel = 2
    #min(sel, i-x) yields 0, 1, 2, 2, 2... for sel = 2
    return ass

def endowment(x, duration, sel=maxsel, interest_rate=0.04, contn = False, rates = am92_rates):
    v = (1+interest_rate)**-1
    mortality = l(x+duration, 0)/l(x, sel)
    return v**duration * mortality

def endo_ass(x, duration, sel = maxsel, interest_rate = 0.04, contn = False, rates = am92_rates):
    return assurance(x, duration, sel, interest_rate, contn, rates) + endowment(x, duration, sel, interest_rate, contn, rates)

def premium():
    prem_type = "annual" #single, annual, quarterly, monthly, continuous
    components = [null(side = "premium", pay_type = "annuity", frequency = "monthly", x = 53, duration = 12, rate = 0.04, table = "AM92", mortality = "select"), #unit = "money" definitionally
                  null(side = "benefit", pay_type = "assurance", x = 65, duration = 0, contn = False, value = 1000, unit = "money"),
                  null(side = "expense", pay_type = "assurance", x = 65, duration = 0, contn = False, value = 10, unit = "money"),
                  null(side = "expense", pay_type = "single", x = 53, value = 0.75, unit = "premium"),
                  null(side = "expense", pay_type = "single", x = 53, value = 150, unit = "money"),
                  null(side = "expense", pay_type = "annuity", frequency = "annual", x = 54, duration = 11, rate = 0.04, value = 0.05, unit = "premium"),
                  null(side = "expense", pay_type = "annuity", frequency = "annual", x = 54, duration = 11, rate = 0.04, value = 10, unit = "money"),
                  ]
    pass

def null(**kwargs):
    pass

def test():
    print("+------------------------+")
    print(f"l_[53]....... =  {l(53):.6f}") #0.962110
    print(f"l_53......... =  {l(53, sel = 0):.6f}") #0.963005
    print("+------------------------+")
    print(f":a_[53]...... = {ann_due(53):.6f}") #16.537994
    print(f":a_53........ = {ann_due(53, sel = 0):.6f}") #16.523642
    print(f":a^(4)_53.... = {ann_due(53, sel = 0, ppy = 4):.6f}") #16.148642
    print("+------------------------+")
    print(f":a_[53]:12... =  {ann_due_temp(x = 53, duration = 12):.6f}") #9.508095
    print(f":a_53:12..... =  {ann_due_temp(x = 53, duration = 12, sel = 0):.6f}") #9.500278
    print(f":a^(4)_53:12. =  {ann_due_temp(x = 53, duration = 12, sel = 0, ppy = 4):.6f}") #9.339830
    print("+------------------------+")
    print(f"A_[53]....... =  {assurance(53):.6f}") #0.363923
    print(f"A_53......... =  {assurance(53, sel = 0):.6f}") #0.364475
    print("+------------------------+")
    print(f"A_[53]:12.... =  {endo_ass(53, 12):.6f}") #0.634304
    print(f"A_53:12...... =  {endo_ass(53, 12, sel = 0):.6f}") #0.634605
