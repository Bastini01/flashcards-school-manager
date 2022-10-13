import pandas as pd
import numpy as np
from dragonmapper import hanzi
from os.path import expanduser

u=expanduser("~")

def getVocSource():
    return pd.read_excel(u+r'\OneDrive\SRL\TechnicalFiles\Dagdai voc 1-5 correct.xlsx')

def getSoundFileDir(vocabUnit):
    b=str(vocabUnit[0])
    c=str(vocabUnit[1]).zfill(2)
    p=str(vocabUnit[2])
    soundFileDir=u+"\OneDrive\SRL\TechnicalFiles\Dangdai audio B1L1 - B3L8\ACICC B"+b+"_L"+c+"_V"+p+" Media\\"
    return soundFileDir

def vuName(vocabUnit):
    return "Book"+str(vocabUnit[0])+"Chapter"+str(vocabUnit[1]).zfill(2)+"-"+str(vocabUnit[2])

def getVu(vocabUnit):
    vun=vuName(vocabUnit)
    vocSource = getVocSource()
    vu = vocSource[vocSource['TextbookChapter'] == vun]
    vu = vu.replace(np.nan, '', regex=True)
    return vu, vun

def getNotes(deckName, vocabUnit, modelName):
    vu = getVu(vocabUnit)[0]
    vun = getVu(vocabUnit)[1]
    notesData = []
    mediaFiles = {'sound':[],'pics':[]}
    for i in range(len(vu.index)):

        noteData = {
                "deckName": deckName,
                "modelName": modelName,
                "fields": {
                    "Traditional": vu.iloc[i]["Traditional Characters"],
                    "PinYin": vu.iloc[i]["PinYin"],
                    "Definition": vu.iloc[i]["Definition (en)"],
                    "Examples": vu.iloc[i]["Examples"].replace("_x000D_", "")
                },
                "options": {
                    "allowDuplicate": True,
                    "duplicateScope": "deck",
                    "duplicateScopeOptions": {
                        "deckName": "Default",
                        "checkChildren": False,
                        "checkAllModels": False
                    }
                },
                "tags": [
                  vun
                ]
            }
        #####Add sound if available
        fileName="B"+ vun[4]+"_L"+vun[12:14]+"_V0"+ vun[-1]+"_"+str(i+1).zfill(2)
        audioLink = vu.iloc[i]["audio link"]
        if audioLink == True:
            audioName = fileName+".mp3"
            noteData['fields']['Sound'] = "[sound:"+audioName+"]"
            mediaFiles['sound'].append(audioName)

        #####Add picture if available
        picLink = vu.iloc[i]["image link"]
        if picLink != '':
            picName = fileName+".jpg"
            noteData['fields']['Examples'] = noteData['fields']['Examples']+'<br><br><img src="'+picName+'">'
            mediaFiles['pics'].append(picName)

        notesData.append(noteData)
    return notesData, mediaFiles

def getNotesMax(deckName, vocabUnit):
    vun=vuName(vocabUnit)
    vocSource = pd.read_excel(r'C:\Users\Pierre-Henry\OneDrive\SRL\TechnicalFiles\Dagdai voc 1-5 correct.xlsx')
    vu = vocSource[vocSource['TextbookChapter'] == vun]
    notesData = []
    for i in range(len(vu.index)):

        noteData = {
                "deckName": deckName,
                "modelName": "Daily vocab",
                "fields": {
                    "Traditional": vu.iloc[i]["Traditional Characters"]+"<br>",
                    "Pinyin": hanzi.to_zhuyin(vu.iloc[i]["Traditional Characters"],
                                              delimiter='', all_readings=False, container='[]'),
                    "English": "<br>"+vu.iloc[i]["Definition (en)"]+"<br>",
                    #"Examples": vu.iloc[i]["Examples"]+"<br><br>"
                },
                "options": {
                    "allowDuplicate": True,
                    "duplicateScope": "deck",
                    "duplicateScopeOptions": {
                        "deckName": "Default",
                        "checkChildren": False,
                        "checkAllModels": False
                    }
                },
                "tags": [
                  vun
                ]
            }
        #####Add sound if available

        notesData.append(noteData)
    return notesData

def getTestNote():

    noteData = {
            "deckName": "Default",
            "modelName": "recall",
            "fields": {
                "Traditional": "實驗",
                "PinYin": "shiyan",
                "Definition": "experiment",
                "Examples": "做實驗",
                "Sound": "[sound:B1_L02_V02_06.mp3]"
            },
            "options": {
                "allowDuplicate": True,
                "duplicateScope": "deck",
                "duplicateScopeOptions": {
                    "deckName": "Default",
                    "checkChildren": False,
                    "checkAllModels": False
                }
            },
            "tags": [
              "test"
            ]
        }

    print(noteData)
    return [noteData]

def chap_filter(nts, chap):
    df = nts[nts['TextbookChapter'].apply(lambda x:x.split("-")[0]
    ) == vuName([chap[0], chap[1], 1]).split('-')[0]]
    return df

def pic_url(nts, chap, word):
    unit = nts[nts['Traditional Characters'] == word]['TextbookChapter'].values[0][-1]
    df = nts[nts['TextbookChapter'].apply(lambda x: x[-1]) == unit].reset_index()
    unit = unit.zfill(2)
    wordNr = str(df.index[df['Traditional Characters'] == word].values[0]+1).zfill(2)
    book = str(chap[0])
    chapter = str(chap[1]).zfill(2)
    url = "http://35.206.234.133/Pictures/B{b}_L{l}_V{v}/B{b}_L{l}_V{v}_{w}.jpg"
    url = url.format(b=book, l=chapter, v=unit, w=wordNr)
    return url

# print(pic_url(getVocSource(), [1, 2], "多"))

#print(getTestNote())
#print(getNotes("Book1Chapter01-1"))
