from os import listdir
from os.path import getmtime
import time
import datetime as dt
time1=time.time()
import anki_db as db
import pandas as pd

def getReviewDataAll():
    revspath = db.technicalFilesPath+'allReviews.pkl'
    if getmtime(revspath) > dt.datetime.now().replace(second=0, hour=0, minute=0).timestamp():       
        return pd.read_pickle(revspath)

    profiles = [x for x in listdir(db.Anki2Dir) if x[0] == "0"]
    allReviews = []
    for i in profiles:
        profNum=int(i[2:5])
        if profNum > 3 and profNum not in [13, 14, 15, 18]:
            profileName = i
            try:allReviews = allReviews+db.getReviews(profileName, dt.date(2021,11,1))
            except Exception as e:
                if "no such table: revlo" in str(e): continue
                print(profileName+" EXCEPTION: extraction issue!", e)
                continue

    df= db.rev_to_df(allReviews)
    df.to_pickle(revspath)   
    return df

# print(len(getReviewDataAll()))