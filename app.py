from genericpath import exists
from MySQLdb import paramstyle
from flask import Flask, render_template, request
import numpy as np

#2 load the words to a dictionary
bisayaDict = []
bisayaDict = open("bisayaWords.txt").read().splitlines()


def levenshteinDistanceDP(token1, token2):
    distances = np.zeros((len(token1) + 1, len(token2) + 1))

    for t1 in range(len(token1) + 1):
        distances[t1][0] = t1

    for t2 in range(len(token2) + 1):
        distances[0][t2] = t2
        
    a = 0
    b = 0
    c = 0
    
    for t1 in range(1, len(token1) + 1):
        for t2 in range(1, len(token2) + 1):
            if (token1[t1-1] == token2[t2-1]):
                distances[t1][t2] = distances[t1 - 1][t2 - 1]
            else:
                a = distances[t1][t2 - 1]
                b = distances[t1 - 1][t2]
                c = distances[t1 - 1][t2 - 1]
                
                if (a <= b and a <= c):
                    distances[t1][t2] = a + 1
                elif (b <= a and b <= c):
                    distances[t1][t2] = b + 1
                else:
                    distances[t1][t2] = c + 2

    #printDistances(distances, len(token1), len(token2))
    return distances[len(token1)][len(token2)]

def printDistances(distances, token1Length, token2Length):
    for t1 in range(token1Length + 1):
        for t2 in range(token2Length + 1):
            print(int(distances[t1][t2]), end=" ")
        print()


#3 for each word get levenstein distance, and update minimum
def getMinimumDistanceWords(token):

    minimumDict = {}
    indexOfMin = 0
    currentMinDistanceVal = levenshteinDistanceDP(bisayaDict[0], token) 
    #print("Minimum: "+bisayaDict[indexOfMin])

    for index in range(1, len(bisayaDict)):
        new_distance = levenshteinDistanceDP(bisayaDict[index], token)
        #print("New distance: {}".format(new_distance))
        
        if new_distance < currentMinDistanceVal :
            indexOfMin = index
            currentMinDistanceVal = new_distance      
            
        index = index+1
        key = bisayaDict[indexOfMin]
        minimumDict[key] = currentMinDistanceVal
        #print("Dict: {}".format(minimumDict))
    print("Dict for LV Distances: {}".format(minimumDict))   
    return minimumDict

def tokenizeInputString(str):
    tokens = str.split()
    return tokens

def wordExistInDict(token):
    if token in bisayaDict:
        return True
    return False

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/getLVDistances")
def getWordDistancesToDict():
    param = request.args.get('reqData')
    listAllDis = getMinimumDistanceWords(param)
    #print("Orig word: "+param)
    #print("All Distances {}".format(listAllDis))
    #topMinDis = listAllDis[-1]
    #print("Top 5: {}".format(topMinDis))
    return listAllDis


@app.route("/spellchecker")
def spellchecker():
    paramStr = request.args.get('reqData')
    tokens = tokenizeInputString(paramStr.lower())    

    result = []

    for token in tokens: 
        #print("Token: "+token)
        if wordExistInDict(token):
            result.append({'word':token,'isInDictionary':True, 'origToken':token, 'closest':''})
            #print("List of Min: {} ".format(result))
        else:            
            listOfMinimum = getMinimumDistanceWords(token)
            closest = list(listOfMinimum)[-1]
            #print("List of Min: {}".format(listOfMinimum) )
            result.append({'word':token,'isInDictionary':False, 'origToken':token, 'closest':closest})

        #print("Result: {}".format(result))
    return result



