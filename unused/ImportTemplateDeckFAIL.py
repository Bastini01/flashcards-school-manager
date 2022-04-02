import os
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

from anki.collection import Collection
from anki.importing.anki2 import Anki2Importer
from anki.importing.apkg import AnkiPackageImporter
from anki.importing.base import Importer
from pprint import pprint


file = "C:\\Users\\Pierre-Henry\\OneDrive\\SRL\\TechnicalFiles\\MTCDeck.apkg"
anki_home = "C:\\Users\\Pierre-Henry\\AppData\\Roaming\\Anki2\\1234"
anki_collection_path = os.path.join(anki_home, "collection.anki2")
col = Collection(anki_collection_path, log=True)

#imp = Anki2Importer(col, file)
#pprint(vars(imp))
#imp.col=col
#imp.dst=col
#imp.file=deckTemplate
#pprint(vars(imp))
pimp = AnkiPackageImporter(col, file)
pimp.dest=col
pimp.run
pprint(vars(pimp))
collog=col.log
print(collog)
#importer.run

print("end")
