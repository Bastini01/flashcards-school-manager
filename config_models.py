
def getFields():
    
    fields=[
        "Definition",
        "Sound",
        "PinYin",
        "Traditional",
        "Examples"
        ]
    return fields

def getTemplates(modelName):

    if modelName=="recall":
        templates=[
        {
                "Name": "recall",
                "Front":
                "<div>{{Definition}}</div>"
                "<br><div style= text-align: left; 'font-family: DFKai-sb, ""Noto Serif TC"", PingFangTC, serif; 'font-size: 25px;'>{{Examples}}</div>",
                "Back":
                "{{FrontSide}}"
                "<hr id=answer>"
                "<div style='font-family: DFKai-sb, KaiU, ""Noto Serif TC"", PingFangTC, serif; font-size: 60px;'>{{Traditional}}</div>"
                "<div style='font-size: 18px;'>{{PinYin}}</div>"
                "<br><div style='font-size: 15px;'>{{Tags}}</div>"
                "<div>{{Sound}}</div>"
            }
        ]

    elif modelName=="dict":
        templates=[
        {
                "Name": "dict",
                "Front":
                "<div>{{Sound}}</div>"
                "<br><div style='font-size: 15px;'>{{Tags}}</div>",
                "Back":
                "{{FrontSide}}"
                "<hr id=answer>"
                "<div style='font-family: DFKai-sb, KaiU, ""Noto Serif TC"", PingFangTC, serif; font-size: 60px;'>{{Traditional}}</div>"
                "<div style='font-size: 18px;'>{{PinYin}}</div>"
                "<div style='font-family: DFKai-sb, KaiU, ""Noto Serif TC"", PingFangTC, serif; 'font-size: 25px;'>{{Examples}}</div>"
                "<div>{{Definition}}</div>"
            }
##        ,
##        {
##                "Name": "recall",
##                "Front":
##                "<div>{{Definition}}</div>"
##                "<div style='font-family: DFKai-sb, KaiU, ""Noto Serif TC"", PingFangTC, serif; 'font-size: 25px;'>{{Examples}}</div>"
##                "<br><div style='font-size: 15px;'>{{Tags}}</div>",
##                "Back":
##                "{{FrontSide}}"
##                "<hr id=answer>"
##                "<div style='font-family: DFKai-sb, KaiU, ""Noto Serif TC"", PingFangTC, serif; font-size: 60px;'>{{Traditional}}</div>"
##                "<div style='font-size: 18px;'>{{PinYin}}</div>"
##                "<div>{{Sound}}</div>"
##            }
        ]

    elif modelName=="reading":
        templates=[
        {
                "Name": "Reading",
                "Front":
                "<div>{{Definition (en)}}</div>"
                "<div style='font-size: 18px;'>{{Examples}}</div>",
                "Back":
                "{{FrontSide}}"
                "<hr id=answer>"
                "<div style='font-family:DFKai-sb; font-size: 26px;'>{{Traditional}}</div>"
                "<div style='font-size: 18px;'>{{PinYin}}</div>"
                "<br><div style='font-size: 15px;'>{{Tags}}</div>"
                "<div>{{Sound}}</div>"
            }
        ]

    return templates
