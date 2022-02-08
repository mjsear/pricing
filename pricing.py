def main():
    import numpy as np
    import pandas as pd
    from functools import lru_cache
    #import time

    #start_time = time.perf_counter()

    with open("data/am92rates.csv") as f: #THIS STUFF HAS TO BE CHANGED TO ALLOW FOR MULTIPLE RATES FILES
        rates = pd.read_csv(f, header=0, index_col=0) #THE COLUMN NAMES SHOULD BE UNUSED, EXCEPT IN IN-PROGRESS COMMANDS

    #print(rates.columns)

    def ann_due(x, sel=len(rates.columns)-1, interest_rate=0.04, ppy=1):
        """
        Returns the expected present value of an lifetime annuity paying amount 1 annually for a life aged x

        Keyword arguments:
        x   -- Age of the life
        sel -- Remaining years of selection 
        interest_rate -- effective annual interest rate
        ppy -- payments per year

        Sel = 0 means ultimate, increasing by one for each year of selection REMAINING.
        Thus, the default sel={number of columns - 1} is a just-selected life [x].
        """
        v = (1+interest_rate)**-1
        adx = 0
        if sel==len(rates.columns)-1:
            col = len(rates.columns)-1
            adx = sum([v**i * l(i, max(col-(i-x), 0)) for i in np.arange(x, 121)])/(v**x * l(x))
        else:
            adx = sum([v**i * l(i, 0) for i in np.arange(x, 121)])/(v**x * l(x,0))
        
        #pthly adjustment:
        adx = adx - (ppy-1)/(2*ppy)
        return adx
    
    def ann_due_temp(x, duration, sel=len(rates.columns)-1, interest_rate=0.04, ppy=1):
        #adxn = ad(x) - [D(x+n)/D(x)]ad(x+n)
        if duration < len(rates.columns) - 1:
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

    @lru_cache(maxsize=None)
    def l(x, sel=len(rates.columns)-1):
        """
        Return the *percentage* of lives still living at age x. 
        
        Keyword arguments:
        x   -- Age of the life
        sel -- Remaining years of selection 

        Sel = 0 means ultimate, increasing by one for each year of selection REMAINING.
        Thus, the default sel={number of columns - 1} is a just-selected life [x].

        This should probably be refactored such that sel=0 means select and sel=len(rates.columns-1) means ultimate, the current definitions are awkward as hell
        """
        if x in rates.index:
            if pd.isna(rates.iloc[:,(len(rates.columns)-1) - sel].loc[x]):
                raise IndexError("Age out of select range")
            else:
                if x == rates.index[0] and sel == 0:
                    return 1
                lx = l(x-1+sel,0)*(1-rates.iloc[:,-1].loc[x-1+sel]) # (x-1) here is the basic unit, we are using the previous q rate to go back one
                for i in range(1, sel+1):
                    lx /= (1-rates.iloc[:,len(rates.columns)-1-i].loc[x+sel-i]) # here we are already starting at the destination, so no -1 is needed
                return lx
        else:
            raise IndexError("Age out of table range")
    
    print(f"l_[53]....... = {l(53):.5f}")
    print(f"l_53......... = {l(53, sel = 0):.5f}")
    print(f":a_[53]...... = {ann_due(53):.5f}")
    print(f":a_53........ = {ann_due(53, sel = 0):.5f}")
    print(f":a^(4)_53.... = {ann_due(53, sel = 0, ppy = 4):.5f}")
    print(f":a_[53]:12... = {ann_due_temp(x = 53, duration = 12):.5f}")
    print(f":a_53:12..... = {ann_due_temp(x = 53, duration = 12, sel = 0):.5f}")
    print(f":a^(4)_53:12. = {ann_due_temp(x = 53, duration = 12, sel = 0, ppy = 4):.5f}")

    #end_time = time.perf_counter()
    #print(f"Execution time: {end_time - start_time}")
    
if __name__ == '__main__':
    main()