import json
import urllib.request
import config_notes
import config_deck
import config_models
from dragonmapper import hanzi
from io import StringIO
from html.parser import HTMLParser
from shutil import copyfile
from os.path import expanduser
import random

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']

def load(profileName):
    invoke('loadProfile', name=profileName)

def sync():
    invoke('sync')

def multi(actions):
    result=invoke('multi', actions=actions)
    return result

def createModel(modelName):
    invoke('createModel',
           modelName=modelName,
           inOrderFields=config_models.getFields(),
           cardTemplates=config_models.getTemplates(modelName)
           )
#createModel('recall')
#createModel('dict')

def updateModel(modelName): #doesn't work
    templ=config_models.getTemplates(modelName)[0]
    invoke('updateModelTemplates',
            model={
                "name": modelName,
                "templates": {
                    templ['Name']: {
                    "Front": templ['Front'],
                    "Back": templ['Back']
                                }
                            }
                }
            )
#print(updateModel('recall'))

def saveDeckConfig(configName):
    
    deckConfig=config_deck.getConfig(configName, 1)
    invoke('saveDeckConfig', config=deckConfig)
#saveDeckConfig('Default')

def deleteDecks(deckNames):
    invoke('deleteDecks', decks=deckNames)

def addMedia(profileName, mediaFiles):
    u=expanduser("~")
    d=u+"\\AppData\\Roaming\\Anki2\\"+profileName+"\\collection.media\\"
    for m in mediaFiles:
        for file in m['sound']:       
            # folderSpec=file[:-9]+file[9]
            vocabUnit=[int(file[1]),int(file[4:6]),int(file[-9:-7])]
            sf=config_notes.getSoundFileDir(vocabUnit)+file
            df=d+file
            copyfile(sf, df)
    
        for file in m['pics']:
            sf=u+"\OneDrive\SRL\TechnicalFiles\Pictures\\"+file[:-7]+"\\"+file
            df=d+file
            copyfile(sf, df)

def addNotesOld(profileName, vocabUnitName, modelName):
    #invoke('loadProfile', name=profileName)
    deckName="當代-"+vocabUnitName[4]+"::第"+vocabUnitName[-4:-2]+"課"
    nts=config_notes.getNotes(deckName, vocabUnitName, modelName)

    addMedia(profileName, nts)
    invoke('addNotes', notes=nts)

def addNotes(profileName, vocabUnit, startChapter=None):
    part1=1
    part2=3
    if not startChapter:
        startChapter=vocabUnit[1]
        part1=vocabUnit[2]
        part2=vocabUnit[2]+1
    nts=[]
    mediaFiles=[]
    
    for i in range(startChapter, vocabUnit[1]+1):
        deckName=config_deck.deckName([vocabUnit[0], i])
        n=[] #notes of one chapter
        m=[] #media files of one chapter
        if vocabUnit[0]>=3:
            invoke('createDeck', deck=deckName)

            for j in range(part1,part2):
                vocabUnit = [vocabUnit[0], i, j]
                print(vocabUnit)
                ra, ma=config_notes.getNotes(deckName, vocabUnit, "recall")
                #random.shuffle(n)
                n.extend(ra)
                m.append(ma)

        if vocabUnit[0]<3:
            deckNameL=deckName+":: 聽"
            invoke('createDeck', deck=deckNameL)
            # m=[]
            d=[]
            for j in range(part1,part2):
                vocabUnit = [vocabUnit[0], i, j]
                # print(vocabUnit)
                da, ma=config_notes.getNotes(deckNameL, vocabUnit, "dict")
                #print(ma)
                d.extend(da)
                m.append(ma)
                #print(m)
            deckNameR=deckName+":: 看"
            invoke('createDeck', deck=deckNameR)
            r=[]
            for j in range(part1,part2):
                # print(j)
                vocabUnit = [vocabUnit[0], i, j]
                # print(vocabUnit)
                ra=config_notes.getNotes(deckNameR, vocabUnit, "recall")[0]
                r.extend(ra)
            n=list(zip(d, r))
            random.shuffle(n)
            n=list(map(list, zip(*n))) #unzip to list of two lists
            n=list(zip(n[0], n[1][len(n[1])//2:]+n[1][:len(n[1])//2])) #split up r, reverse two parts and zip with d 
            n=[item for sublist in list(n) for item in sublist] #turn list of tuples into flat list
        
        nts.extend(n)
        mediaFiles.extend(m)
        #print(mediaFiles)
    random.shuffle(nts)    
    addMedia(profileName, mediaFiles)
    invoke('addNotes', notes=nts)
#addNotes("00001 Outlook PH",[1,5,2], 5)
        
def addNotesCustom(vocabUnit, profileName):
    if profileName=="00015 Max Max":
        deckName="馬克斯::當代五::第"+str(vocabUnit[1]).zfill(2)+"課"
        invoke('createDeck', deck=deckName)
        invoke('addNotes', notes=config_notes.getNotesMax(deckName, vocabUnit))

# l=[[5, 5, 1], [5, 5, 2], [5, 6, 1], [5, 6, 2], [5, 7, 1], [5, 7, 2], [5, 8, 1], [5, 8, 2], [5, 9, 1], [5, 9, 2], [5, 10, 1], [5, 10, 2]]
# for i in l:
#     addNotesCustom(i, "00015 Max Max")


def updateNotes_pinyinToZhuyin(query):
    q=query
    noteIds=invoke('findNotes', query=q)
    nInfo=invoke('notesInfo', notes=noteIds)
    for n in nInfo:
        n['id']=n.pop('noteId')
        del n['modelName'], n['tags'], n['cards']
        #print(n)
        f={}
        for i in n['fields'].items():
            #print(f)
            f.update({i[0]: i[1]['value']})
        #print(f)
        n['fields']=f
        t=n['fields']['Traditional']
        #print(t)
        z="<br><div style='font-size: 18px;'>"+hanzi.to_zhuyin(t, delimiter='', all_readings=False, container='[]')
        n['fields']['Pinyin']=z
        #print(n)
        invoke('updateNoteFields', note=n)
        print(nInfo.index(n),"/",len(nInfo))

def updateNotes_stripHtml(query):
    q=query
    noteIds=invoke('findNotes', query=q)
    nInfo=invoke('notesInfo', notes=noteIds)
    for n in nInfo:
        n['id']=n.pop('noteId')
        del n['modelName'], n['tags'], n['cards']
        #print(n)
        f={}
        for i in n['fields'].items():
            #print(f)
            f.update({i[0]: i[1]['value']})
        #print(f)
        n['fields']=f
        html=n['fields']['Traditional']
        #print(t)
        #html="<div style='font-family: DFKai-sb, KaiU, serif; font-size: 60px;'>"+nohtml
        nohtml=strip_tags(html)
        n['fields']['Traditional']=nohtml
        #print(n)
        invoke('updateNoteFields', note=n)
        print(nInfo.index(n),"/",len(nInfo))

def updateNoteTest():

    n={'fields': {
        'Definition': 'The Bakery World Cup',
        'Sound': '[sound:B3_L08_V02_45.mp3]',
        'PinYin': "<br><div style='font-size: 18px;'>ㄕˋ ㄐㄧㄝˋ ㄇㄧㄢˋ ㄅㄠ ㄉㄚˋ ㄙㄞˋ",
        'Traditional': '世界麵包大賽',
        'Examples': '2016年的[...]是哪一個國家拿到冠軍？<br><br><img src="B3_L08_V02_45.jpg">'}, 'id': 1637209707903}
    invoke('updateNoteFields', note=n)

# def prepProfileMulti(profileName, modelName, vocabUnitName): #doesn't work!!!!!!
#     result=multi([
#         {"action": "loadProfile", "params": {"name": profileName}},
#         {"action": "createModel", "params": [{"modelName": modelName},
#                                              {"inOrderFields": config_models.getFields()},
#                                              {"cardTemplates": config_models.getTemplates(modelName)}
#                                              ]
#          },
#         {"action": "saveDeckConfig", "params": {"config": "deckConfig"}},
#         {"action": "setDeckConfigId", "params": [{"decks": deckName}, {"deckConfigId": deckConfigId}]},
#         {"action": "addNotes", "params": {"notes": config_notes.getNotes(vocabUnitName, modelName)}}
#          ])
#     return result

def prepProfile(profileName, vocabUnit, startChapter=None):
    load(profileName)
    createModel("recall")
    createModel("dict")
    deckConfig=config_deck.getConfig('Default', 1)
    invoke('saveDeckConfig', config=deckConfig)
    #invoke('setDeckConfigId', decks='Default', configId=1)
    addNotes(profileName, vocabUnit, startChapter)

#prepProfile("00038 Emma Forbes", [1,8,2], 6)   
    
    
#sync()
#print(invoke('getDeckConfig', deck='當代-1'))
##deckConfig=config_deck.getConfig('當代-1', 1)
##invoke('saveDeckConfig', config=deckConfig)
#print(invoke("addNotes", notes=config_notes.getTestNote()))
#addNotes("00003 hotmail PH", "Book1Chapter05-1", "recall")
#updateNoteTest()
#updateNotes_pinyinToZhuyin("deck:馬克斯::當代五 is:new") #deck:馬克斯::當代五
#updateNotes_stripHtml("deck:馬克斯::當代五 is:new") #deck:馬克斯::當代五
#print(invoke('deckNames'))
#ProfileList=invoke('getProfiles')
#load("2 Estiem PH")

