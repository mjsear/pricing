from cmath import nan


def main():
    import numpy as np
    import pandas as pd

    with open("D:\\Downloads\\am92rates.csv") as f:
        rates = pd.read_csv(f, header=0, names = ["sel","sel-1","ult"], index_col=0)

    rates.rename(columns = {"q[x]":"sel", "q[x-1]+1":"sel-1"}, inplace = True)
    rates.columns

    def annuity_due(x, sel=len(rates.columns)-1):
        v = 1.04**-1
        axd = 0
        if sel==len(rates.columns)-1:
            for i in range(len(rates.columns)-1):
                coef = 1
                for j in range(i):
                    coef *= (1-rates.iloc[j,j])
                axd += coef * v**(x+i) * l(x)
            axd += sum([1.04**(-1*i)*l(i,0) for i in np.arange(x+(len(rates.columns)-1),121,1)])
            axd /= v**x * l(x)
            #v**(x+0) * l(x) + 
            #v**(x+1) * l(x) * (1-rates.iloc[0,0]) + 
            #v**(x+2) * l(x) * (1-rates.iloc[0,0]) * (1-rates.iloc[1,1])
        else:
            axd = sum([1.04**(-1*i)*l(i, 0) for i in np.arange(x,121,1)])/(v**x * l(x,0))
        return axd
    annuity_due(80)
    
    # product
    def l(x, sel=len(rates.columns)-1):
        """
        This should probably be refactored such that sel=0 means select and sel=len(rates.columns-1) means ultimate, all these definitions are currently awkward as hell
        sel = 0 for ultimate mortality, sel = len(rates.columns)-1 for select mortality, sel = between those for years since selection
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

    print(annuity_due(55))


if __name__ == '__main__':
    main()
