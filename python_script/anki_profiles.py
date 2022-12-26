from os.path import expanduser, join
from datetime import datetime as dt, timedelta as tdelta
from shutil import copyfile
import random
from pprint import pprint
from aqt.profiles import ProfileManager
from anki.db import DB  ### anki.db EDITED for multithreading --> sqlite.connect(path, timeout=timeout, check_same_thread=False)
from anki.collection import Collection
from anki.decks import DeckManager
from anki.models import ModelManager
from anki.utils import intTime, fieldChecksum
from anki.notes import Note
import config_models, config_deck, config_notes
# import anki
# print(anki.__file__)

today=dt.now().date()
u=expanduser("~")
ankiDir=u+"\\AppData\\Roaming\\Anki2\\"
pm = ProfileManager()
db=DB(ankiDir+"prefs21.db")
pm.db=db

def getProfiles():
    profiles = pm.profiles()
    return profiles

def loadProfile(profileName):
    pm.setupMeta()
    pm.openProfile(profileName)
    pm.ensureBaseExists()
    pm.profileFolder()
    pm.addonFolder()
    pm.backupFolder()
    pm.collectionPath()

def getCollection(profileName):
    anki_home = ankiDir+profileName
    anki_collection_path = join(anki_home, "collection.anki2")
    col = Collection(anki_collection_path, log=True)
    return col

def createModel(profileName, modelName, css = None, isCloze = False):
        inOrderFields = config_models.getFields()
        cardTemplates = config_models.getTemplates(modelName)
        if type(profileName) == str:
            collection = getCollection(profileName)
        else: collection = profileName
        mm = ModelManager(collection)

        if len(inOrderFields) == 0:
            raise Exception('Must provide at least one field for inOrderFields')
        if len(cardTemplates) == 0:
            raise Exception('Must provide at least one card for cardTemplates')
        if modelName in mm.all_names_and_ids():
            raise Exception('Model name already exists')


        # Generate new Note
        m = mm.new(modelName)
        if isCloze:
            m['type'] = 0

        # Create fields and add them to Note
        for field in inOrderFields:
            fm = mm.new_field(field)
            mm.add_field(m, fm)

        # Add shared css to model if exists. Use default otherwise
        if (css is not None):
            m['css'] = css

        # Generate new card template(s)
        cardCount = 1
        for card in cardTemplates:
            cardName = 'Card ' + str(cardCount)
            if 'Name' in card:
                cardName = card['Name']

            t = mm.new_template(cardName)
            cardCount += 1
            t['qfmt'] = card['Front']
            t['afmt'] = card['Back']
            mm.add_template(m, t)

        mm.add(m)
        collection.save()
        return m

def createDeck(profileName, deckName):
    collection = getCollection(profileName)
    collection.decks.id(deckName)
    collection.save()
    return

def saveDeckConfig(profileName, config):
        collection = getCollection(profileName)

        config['id'] = str(config['id'])
        config['mod'] = intTime()
        config['usn'] = collection.usn()
        if int(config['id']) not in [c['id'] for c in collection.decks.all_config()]:
            return False
        try:
            collection.decks.save(config)
            collection.decks.update_config(config)
        except:
            return False
        collection.save()
        return True

def connectProfile(profileName, email, oth):
    userName=email
    password = oth if oth else email.split("@")[0]
    col = getCollection(profileName)
    try:
        auth=col.sync_login(userName, password)
    except Exception as e:
        print(profileName, e)
        return False
    loadProfile(profileName)
    pm.set_host_number(auth.host_number)
    pm.set_sync_key(auth.hkey)
    pm.set_sync_username(userName)
    pm.save()
    # col.save()
    # col.close()
    return True

def SetAutoSyncAll(choice=False): #sets the 'autosync on open' setting for all profiles 
    for profileName in getProfiles():
        pm.setupMeta()
        pm.openProfile(profileName)
        pm.profileFolder()
        pm.profile["autoSync"]=choice
        pm.save()
        print(profileName+" auto sync: ", choice)

def sync(profileName):
    col = getCollection(profileName)
    pm.openProfile(profileName)
    SyncAuth=pm.sync_auth()
    col.db.commit()
    try:
        c=col.sync_collection(SyncAuth)
        m=col.sync_media(SyncAuth)
    except Exception as e:
        if '423' in str(e):
            print(profileName+" SYNC ERROR (account not activated)", e)
            return 'not activated'
        else: print(profileName+" SYNC ERROR", e); return 'nok' 
    #Handle full sync required cases
    if len(c.ListFields())>1: 
        if c.ListFields()[1][1]==2 or c.ListFields()[1][1]==3:
            c=col.full_download(SyncAuth)
            print(profileName+" FULL DOWNLOAD COMPLETE\n")
            # return "fullSync"
        else: 
            print(profileName+" FULL SYNC REQUIRED\n", c)
            return "fullSync"
    ##################""
    col.save()
    col.close()
    return 'ok'    

def first_sync(profileName):
    col = getCollection(profileName)
    pm.openProfile(profileName)
    SyncAuth=pm.sync_auth()
    col.db.commit()
    col.full_download(SyncAuth)
    col.save()
    col.close()
    return

def prep_profile(profileName):
    createModel(profileName, "dict")
    createModel(profileName, "recall")
    saveDeckConfig(profileName, config_deck.getConfig('Default', 1))

def getSyncStatus(profileName):
    col = getCollection(profileName)
    pm.openProfile(profileName)
    SyncAuth=pm.sync_auth()
    try:
        result=col.sync_status(SyncAuth)
    except:
        print("Sync status "+profileName+": FAILED")
        return "con fail"
    if not result:
        print("Sync status "+profileName+": UP TO DATE")
        return "con succ"
    print("Sync status "+profileName+": "+str(result))
    return "con succ"

def get_all_syncStatus():
    for profileName in getProfiles():
        getSyncStatus(profileName)

def reminder_schedule(status, statusDate, forceConnect):
    s=None
    if status[-1]=='x': return None
    if status[:3]=='new' or status=='active': s='0'
    elif forceConnect: s=status[-1]
    elif status[-1]=='0' and today >= statusDate+tdelta(days=1): s='1'        
    elif status[-1]=='1' and today >= statusDate+tdelta(days=1): s='2'
    elif status[-1]=='2' and today >= statusDate+tdelta(days=1): s='3'
    elif status[-1]=='3' and today >= statusDate+tdelta(days=4): s='4'
    elif status[-1]=='4' and today >= statusDate+tdelta(days=7): s='5'
    elif status[-1]=='5' and today >= statusDate+tdelta(days=15): s='x'
    return s


def handle_connection(profileName, email, status, statusDate, oth, forceConnect=False):
    s = reminder_schedule(status, statusDate, forceConnect)
    if s:
        con=connectProfile(profileName, email, oth)
        if con==True: return True
    return s

def handle_not_activated(status, statusDate, forceConnect=False):
    return reminder_schedule(status, statusDate, forceConnect)

def createNote(collection, note):

        model = collection.models.by_name(note['modelName'])
        if model is None:
            try: createModel(collection, note['modelName']) 
            except: raise Exception('model was not found: {}'.format(note['modelName']))

        deck = collection.decks.by_name(note['deckName'])
        if deck is None:
            raise Exception('deck was not found: {}'.format(note['deckName']))

        ankiNote = Note(collection, model)
        ankiNote.note_type()['did'] = deck['id']
        if 'tags' in note:
            ankiNote.tags = note['tags']

        for name, value in note['fields'].items():
            for ankiName in ankiNote.keys():
                if name.lower() == ankiName.lower():
                    ankiNote[ankiName] = value
                    break

        allowDuplicate = False
        duplicateScope = None
        duplicateScopeDeckName = None
        duplicateScopeCheckChildren = False
        duplicateScopeCheckAllModels = False

        if 'options' in note:
            options = note['options']
            if 'allowDuplicate' in options:
                allowDuplicate = options['allowDuplicate']
                if type(allowDuplicate) is not bool:
                    raise Exception('option parameter "allowDuplicate" must be boolean')
            if 'duplicateScope' in options:
                duplicateScope = options['duplicateScope']
            if 'duplicateScopeOptions' in options:
                duplicateScopeOptions = options['duplicateScopeOptions']
                if 'deckName' in duplicateScopeOptions:
                    duplicateScopeDeckName = duplicateScopeOptions['deckName']
                if 'checkChildren' in duplicateScopeOptions:
                    duplicateScopeCheckChildren = duplicateScopeOptions['checkChildren']
                    if type(duplicateScopeCheckChildren) is not bool:
                        raise Exception('option parameter "duplicateScopeOptions.checkChildren" must be boolean')
                if 'checkAllModels' in duplicateScopeOptions:
                    duplicateScopeCheckAllModels = duplicateScopeOptions['checkAllModels']
                    if type(duplicateScopeCheckAllModels) is not bool:
                        raise Exception('option parameter "duplicateScopeOptions.checkAllModels" must be boolean')

        duplicateOrEmpty = isNoteDuplicateOrEmptyInScope(
            ankiNote,
            deck,
            collection,
            duplicateScope,
            duplicateScopeDeckName,
            duplicateScopeCheckChildren,
            duplicateScopeCheckAllModels
        )

        if duplicateOrEmpty == 1:
            raise Exception('cannot create note because it is empty')
        elif duplicateOrEmpty == 2:
            if allowDuplicate:
                return ankiNote
            raise Exception('cannot create note because it is a duplicate')
        elif duplicateOrEmpty == 0:
            return ankiNote
        else:
            raise Exception('cannot create note for unknown reason')

def addNote(collection, note):
        ankiNote = createNote(collection, note)
        collection.add_note(ankiNote, ankiNote.note_type()["did"])
        return ankiNote.id

def addNotes(profileName, notes):
    results = []
    collection = getCollection(profileName)

    for note in notes:
        # try:
        results.append(addNote(collection, note))
        # except: pass
    collection.save()
    return results

def isNoteDuplicateOrEmptyInScope(note, deck, collection, duplicateScope,
    duplicateScopeDeckName,
    duplicateScopeCheckChildren,
    duplicateScopeCheckAllModels):
    # Returns: 1 if first is empty, 2 if first is a duplicate, 0 otherwise.

    # note.dupeOrEmpty returns if a note is a global duplicate with the specific model.
    # This is used as the default check, and the rest of this function is manually
    # checking if the note is a duplicate with additional options.
    if duplicateScope != 'deck' and not duplicateScopeCheckAllModels:
        return note.dupeOrEmpty() or 0

    # Primary field for uniqueness
    val = note.fields[0]
    # if not val.strip(): #leads to bug if the sound field happens to be first and empty...
    #     return 1
    csum = fieldChecksum(val)

    # Create dictionary of deck ids
    dids = None
    if duplicateScope == 'deck':
        did = deck['id']
        if duplicateScopeDeckName is not None:
            deck2 = collection.decks.by_name(duplicateScopeDeckName)
            if deck2 is None:
                # Invalid deck, so cannot be duplicate
                return 0
            did = deck2['id']

        dids = {did: True}
        if duplicateScopeCheckChildren:
            for kv in collection.decks.children(did):
                dids[kv[1]] = True

    # Build query
    query = 'select id from notes where csum=?'
    queryArgs = [csum]
    if note.id:
        query += ' and id!=?'
        queryArgs.append(note.id)
    if not duplicateScopeCheckAllModels:
        query += ' and mid=?'
        queryArgs.append(note.mid)

    # Search
    for noteId in note.col.db.list(query, *queryArgs):
        if dids is None:
            # Duplicate note exists in the collection
            return 2
        # Validate that a card exists in one of the specified decks
        for cardDeckId in note.col.db.list('select did from cards where nid=?', noteId):
            if cardDeckId in dids:
                return 2

    # Not a duplicate
    return 0

def addMedia(profileName, mediaFiles):
    u=expanduser("~")
    d=u+"\\AppData\\Roaming\\Anki2\\"+profileName+"\\collection.media\\"
    for m in mediaFiles:
        for file in m['sound']:       
            vocabUnit=[int(file[1]),int(file[4:6]),int(file[-9:-7])]
            sf=config_notes.getSoundFileDir(vocabUnit)+file
            df=d+file
            copyfile(sf, df)
    
        for file in m['pics']:
            sf=u+"\OneDrive\SRL\TechnicalFiles\Pictures\\"+file[:-7]+"\\"+file
            df=d+file
            copyfile(sf, df)

def add_notes(profileName, vocabUnit, startChapter=None):
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
            createDeck(profileName, deckName)

            for j in range(part1,part2):
                vocabUnit = [vocabUnit[0], i, j]
                ra, ma=config_notes.getNotes(deckName, vocabUnit, "recall")
                #random.shuffle(n)
                n.extend(ra)
                m.append(ma)

        if vocabUnit[0]<3:
            deckNameL=deckName+":: 聽"
            createDeck(profileName, deckNameL)
            # m=[]
            d=[]
            for j in range(part1,part2):
                vocabUnit = [vocabUnit[0], i, j]
                da, ma=config_notes.getNotes(deckNameL, vocabUnit, "dict")
                d.extend(da)
                m.append(ma)
            deckNameR=deckName+":: 看"
            createDeck(profileName, deckNameR)
            r=[]
            for j in range(part1,part2):
                vocabUnit = [vocabUnit[0], i, j]
                ra=config_notes.getNotes(deckNameR, vocabUnit, "recall")[0]
                r.extend(ra)
            n=list(zip(d, r))
            random.shuffle(n)
            n=list(map(list, zip(*n))) #unzip to list of two lists
            n=list(zip(n[0], n[1][len(n[1])//2:]+n[1][:len(n[1])//2])) #split up r, reverse two parts and zip with d 
            n=[item for sublist in list(n) for item in sublist] #turn list of tuples into flat list
        
        nts.extend(n)
        mediaFiles.extend(m)
    random.shuffle(nts)    
    addMedia(profileName, mediaFiles)
    nrAdded=len(addNotes(profileName, nts))
    if nrAdded == len(nts): 
        return True
    return False

def deleteDeck(profileName, vocabUnit):
    col = getCollection(profileName)
    dm = DeckManager(col)
    deckName = config_deck.deckName(vocabUnit)
    did=dm.id_for_name(deckName)
    result=dm.remove([did])
    col.save()
    print(profileName, vocabUnit, "removed")

def createBlankProfile(profileName):

    if profileName[5:] in getProfiles() or profileName in getProfiles():
        raise Exception("Duplicate profile")
    pm.create(profileName)
    loadProfile(profileName)
    pm.profile["autoSync"]=False
    pm.save()
    
    return True

def createProfile(profileName):

    created=createBlankProfile(profileName)
    if created==False: 
        print(profileName+" DUPLICATE")
        return False

    return True


         

