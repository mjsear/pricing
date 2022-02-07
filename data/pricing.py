def main():
    import numpy as np
    import pandas as pd

    with open("am92rates.csv") as f: #THIS STUFF HAS TO BE CHANGED TO ALLOW FOR MULTIPLE RATES FILES
        rates = pd.read_csv(f, header=0, names = ["sel","sel-1","ult"], index_col=0) #THE COLUMN NAMES SHOULD BE UNUSED, EXCEPT IN IN-PROGRESS COMMANDS

    rates.rename(columns = {"q[x]":"sel", "q[x-1]+1":"sel-1"}, inplace = True)
    rates.columns

    def annuity_due(x, sel=len(rates.columns)-1):
        """
        Returns the expected present value of an lifetime annuity paying amount 1 annually for a life aged x

        Keyword arguments
        x   -- Age of the life
        sel -- Remaining years of selection 

        Sel = 0 means ultimate, increasing by one for each year of selection REMAINING.
        Thus, the default sel={number of columns - 1} is a just-selected life [x].
        """
        v = 1.04**-1
        axd = 0
        if sel==len(rates.columns)-1:
            col = len(rates.columns)-1
            axd = sum([v**i * l(i, max(col-(i-x), 0)) for i in np.arange(x, 121)])/(v**x * l(x))
        else:
            axd = sum([v**i * l(i, 0) for i in np.arange(x, 121)])/(v**x * l(x,0))
        return axd

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
                lx = l(x-1+sel,0)*(1-rates['ult'].loc[x-1+sel]) # (x-1) here is the basic unit, we are using the previous q rate to go back one
                for i in range(1, sel+1):
                    lx /= (1-rates.iloc[:,len(rates.columns)-1-i].loc[x+sel-i]) # here we are already starting at the destination, so no -1 is needed
                return lx
        else:
            raise IndexError("Age out of table range")
    
    print(f"l_[53] = {l(53)}")
    print(f"l_53 = {l(53,0)}")
    print(f":a_[53] = {annuity_due(53)}")
    print(f":a_53 = {annuity_due(53,0)}")

if __name__ == '__main__':
    main()