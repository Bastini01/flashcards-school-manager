import sys
from time import time
from datetime import time, datetime
time1=time()
import random
import re
def fib(n):    # write Fibonacci series up to n
    a, b = 0, 1
    while a < n:
        #print(a, end=' ')
        print(a, ' ')
        a, b = b, a+b
    print()

def fib2(n):   # return Fibonacci series up to n
    result = []
    a, b = 0, 1
    while a < n:
        result.append(a)
        a, b = b, a+b
    return result

def test(n):
    print ("blabla"[2:])
    abc=["a", "b", "c"]
    if "g" in abc or "f" in abc:
        for i in range(n):
            print("Profile created (",(i+1),"/",n,")")
            profileName=str(i+1)+" "+" "
            print(profileName)

def test1(string):
    integer=int(string[0:5])
    print(integer)
    print(integer*5)

def millitotimestamp(milli):
    stamp=datetime.fromtimestamp(milli/1000.0)
    print(stamp)

def rangetest(a,b):
    rg = list(range(a,b))
    print(rg)

def ziptest():
    zipped = [("a", 1), ("b", 2)]
    unzipped_object = zip(*zipped)
    unzipped_list = list(unzipped_object) #Separate paired elements in tuple to separate tuples.
    print(unzipped_list)

def ziptest2():
    d=['d1','d2','d3','d4']
    r=['r1','r2','r3','r4']
    dr=list(zip(d, r))
    random.shuffle(dr)
    dr=list(map(list, zip(*dr))) #unzip to list of two lists
    dr=list(zip(dr[0], dr[1][len(dr[1])//2:]+dr[1][:len(dr[1])//2])) #split up r, reverse two parts and zip with d 
    dr=[item for sublist in list(dr) for item in sublist] #turn list of tuples into flat list
    print(dr)

def splittest():
    A = [1,2,3,4,5,6, 7, 8]
    print(A[:len(A)//2])
    print(A[len(A)//2:])

def regexChapter(txt):
    reg = r'Book[1-5]Chapter[0-1][0-9]'
    r=re.search(reg, txt)
    if not r: return None
    else: return r.group(0)
# (regexChapter("Something esle"))

def iftest():
    c="f"
    a="c"
    # b="l"
    if a=="c" or (a=="h" and b==True):
        print('ok')






