import os

from anki.collection import Collection

# Find the Anki directory 
anki_home = "C:\\Users\\Pierre-Henry\\AppData\\Roaming\\Anki2\\PHOutlook"
anki_collection_path = os.path.join(anki_home, "collection.anki2")

# 1. Load the anki collection 
col = Collection(anki_collection_path, log=True)
#col = Collection(anki_collection_path, backend=_RustBackend)

# 2. Select the deck 

# Find the model to use (Basic, Basic with reversed, ...)
print(col.models.all_names_and_ids())
modelBasic = col.models.by_name('Basic')
# Set the deck
deck = col.decks.by_name('Default')
col.decks.select(deck['id'])
col.decks.current()['mid'] = modelBasic['id']

# 3. Create a new card 
note = col.newNote()
note.fields[0] = "test2" # TraditionalChar
note.fields[1] = "test3"   # PinYin
note.fields[2] = "Test4"   # Definition (en)
note.fields[3] = "test5"   # Examples
#col.add_note(note, deck['id'])

# 4. Save changes 
#col.save()
print("end")
