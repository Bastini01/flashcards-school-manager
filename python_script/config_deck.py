
def deckName(vocabUnit):
    return "當代-"+str(vocabUnit[0])+"::第"+str(vocabUnit[1]).zfill(2)+"課"

def getConfig(deckName, configId):
    config= {
                "lapse": {
                    "leechFails": 8,
                    "delays": [10],
                    "minInt": 1,
                    "leechAction": 1,
                    "mult": 0
                },
                "dyn": False,
                "autoplay": True,
                "mod": 1640857232,
                "id": configId,
                "maxTaken": 180,
                "new": {
                    "bury": True,
                    "order": 1,
                    "initialFactor": 2500,
                    "perDay": 1000,
                    "delays": [5],
                    "separate": True,
                    "ints": [5, 10, 7]
                },
                "name": deckName,
                "rev": {
                    "bury": True,
                    "ivlFct": 1,
                    "ease4": 2.0,
                    "maxIvl": 36500,
                    "perDay": 1000,
                    "minSpace": 1,
                    "fuzz": 0.05
                },
                "timer": 0,
                "replayq": True,
                "usn": -1
            }
    return config
