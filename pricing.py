def main():
    import numpy as np
    import pandas as pd

    with open("D:\\Downloads\\am92rates.csv") as f:
        rates = pd.read_csv(f, header=0, names = ["sel","sel-1","ult"], index_col=0)

    rates.rename(columns = {"q[x]":"sel", "q[x-1]+1":"sel-1"},inplace = True)
    rates.columns

    def annuity_due(x):
        v = 1.04
        if rates.Age.iloc[0] <= x <= rates.Age.iloc[-1]:
            
            start = 1+x-rates.Age[0]
            epv = 1
            for i in range(103-start):
                epv += v**(-i) * (1-rates.qx.iloc[start+i])
            print(start)
            print(rates.Age.iloc[start])
            return epv
        else:
            print("Age out of range")
            return

    # product
    def l(x, sel):
        if x in rates.index:
            if sel == "ult":
                return (1-rates.iloc[0:(x-rates.index[0]),-1:]).prod(axis=0)
            elif sel == "sel":
                lx = (1-rates["ult"].loc[x+len(rates.columns)-1]).prod(axis=0) #We go from 0 to (x-age[0]) plus extra steps for each select year, minus 1 for the ult year
                for i in range(1,len(rates.columns)):
                    lx /= (1-rates.iloc[x-rates.index[0]+len(rates.columns)-1-i,-1-i]) #Then we divide out the select q's to get back up from x+select to [x]
                return lx
        else:
            raise IndexError("Age out of table range")

    print(annuity_due(55))

np.



if __name__ == '__main__':
    main()

