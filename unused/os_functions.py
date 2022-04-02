from os import listdir, rename, remove
from os.path import isfile, join
import re
from shutil import copyfile
from PIL import Image
# mypath= r"C:\Users\Pierre-Henry\OneDrive\SRL\TechnicalFiles\Pictures\B3_L08_V02"
mypath= r"C:\Users\Pierre-Henry\OneDrive\SRL\Student lists\220304\classes"
pdfdest = r"C:\Users\Pierre-Henry\OneDrive\SRL\Student lists\220304\classes"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
# print(onlyfiles)

def regex(txt):
   return re.search("^(?:(?!\d\d).)*(\d\d)", txt)

def copy_and_rename():
   for i in [i+5 for i in range(8)]:
      srcdir=r"C:\Users\Pierre-Henry\OneDrive\SRL\TechnicalFiles\田老師PPT\當代四\L"+str(i)
      dstdir=r"C:\Users\Pierre-Henry\OneDrive\SRL\TechnicalFiles\Pictures\Edited ppts\4册"
      for j in range(2):
         copyfile(join(srcdir, listdir(srcdir)[j]),dstdir+"\B4_L"+str(i).zfill(2)+"_V"+str(j+1).zfill(2)+".pptx")
# copy_and_rename()

def rename():
   o=40
   for f in onlyfiles:
      # chapter = f.split('-')[0][-2:]
      # part = f.split('-')[1][0].zfill(2)
      # newName="B"+mypath[-2]+"_L"+chapter+"_V"+part+".pptx"
      if str(o) in f:
         n=o-1
         newName = f.replace(str(o), str(n))
         rename(join(mypath, f), join(mypath, newName))
         print(newName)
         o=o+1

def delete():
   for f in onlyfiles:
      if f[-3:]=='pdf': remove(join(mypath, f))
# delete()

def convert_to_pdf():
   for f in onlyfiles:
      image1 = Image.open(join(mypath, f))
      im1 = image1.resize((3233, 2425))
      im1 = im1.convert('RGB')
      im1.save(join(pdfdest, f.replace('jpg', 'pdf')))
# convert_to_pdf()
   