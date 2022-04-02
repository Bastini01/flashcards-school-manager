#rename extracted and ordered pictures from 田老師's slides

import os

#### variables
unit="B3_L09_V01"
unitNumberOfWords= 30
toIgnore = [2,28]
######
d=os.path.expanduser("~")+"\OneDrive\SRL\TechnicalFiles\Pictures\\"+unit
filelist = os.listdir(d) 



############ GET A LIST OF FILENAMES ORDERED BY NUMBER
def getnumber(inputString): #get number out of file name
    l=[char for char in inputString if char.isdigit()]
    string=""
    for i in l:
        string=string+i
    return int(string)

def getlistofnum(): 
    listofnum=[]
    for i in filelist:
        listofnum.append(getnumber(i))
    return listofnum

k=getlistofnum()
dictio = {k[i]: filelist[i] for i in range(len(k))}
dictio = {k: v for k, v in sorted(dictio.items(), key=lambda item: item[0])}

orderedfiles = [i for i in list(dictio.values())]
#############
words=[]
for i in range(unitNumberOfWords):
    if i+1 in toIgnore:
        continue
    words.append(i+1)

if len(words)!=len(dictio):
    print("number of words and images don't match")
    quit()

for i, j in zip(words, orderedfiles):
    os.rename(d+"\\"+j, d+"\\"+unit+"_"+str(i).zfill(2)+".jpg")
    print("done")



