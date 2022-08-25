from os import listdir
from os.path import getmtime
import time
import datetime as dt
time1=time.time()
import anki_db as db
import mtc_info
import pandas as pd

def termFilter(df, term):
    if term=='all': return df
    else:
        df = df[(df['reviewTime'].dt.date >= mtc_info.get_term_dates(term)['termStart']) &
                (df['reviewTime'].dt.date < mtc_info.get_term_dates(term)['termEnd'])]
    return df

def getReviewDataAll(term='all'):
    revspath = db.technicalFilesPath+'allReviews.pkl'
    try: 
        if getmtime(revspath) > dt.datetime.now().replace(second=0, hour=0, minute=0).timestamp():       
            return termFilter(pd.read_pickle(revspath), term)
    except: pass

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

    df = db.rev_to_df(allReviews)
    df.to_pickle(revspath)   
    return termFilter(df, term)

