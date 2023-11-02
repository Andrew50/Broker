import pandas as pd
import os
import shutil





class consolidate:
    def consolidate():





        path = "C:/Screener/tmp/subsetups/"

        dir_list = os.listdir(path)


        try:
            setups = pd.read_feather(r"C:\Screener\sync\setups.feather")
        except:
            setups = pd.DataFrame()


        todays_setups = pd.DataFrame()


        if len(dir_list) > 0:
            for f in dir_list:
                if "today" in f:
                    df = pd.read_feather(path + f)
                    todays_setups = pd.concat([todays_setups,df])
                else:
                    
                    df = pd.read_feather(path + f)
                    setups = pd.concat([setups,df])

        
            
            if not setups.empty:
                setups.reset_index(inplace = True,drop = True)
                setups.to_feather(r"C:\Screener\sync\setups.feather")

        
            if not todays_setups.empty:
                todays_setups.reset_index(inplace = True,drop = True)
                todays_setups.to_feather(r"C:\Screener\sync\todays_setups.feather")


        if os.path.exists("C:/Screener/tmp/subsetups"):
            shutil.rmtree("C:/Screener/tmp/subsetups")
        os.mkdir("C:/Screener/tmp/subsetups")




if __name__ == '__main__':
    consolidate.consolidate()










