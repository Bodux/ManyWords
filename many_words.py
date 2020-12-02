import csv
import random
import hashlib
import os
from datetime import datetime, timedelta

BUILD = "0.4"
SETDIR_PATH = "./sets"

class ManyWords:
    SECONDS_PER_WORD = 15
    FIELDS = ['DE GF', 'FR GF', '1PS', '2PS', '3PS', '1PP', '2PP', '3PP', '1PS PC']
    FIELD_LABELS = {
        'DE GF': "Grundform DE",
        'FR GF': "Grundform FR",
        '1PS': 'je',
        '2PS': 'tu',
        '3PS': 'il/elle',
        '1PP': 'nous',
        '2PP': 'vous',
        '3PP': 'ils/elles',
        '1PS PC': 'Passé composé:'
    }
    assert (FIELD_LABELS.keys() == set(FIELDS))

    def __init__(self, wordList):
        trimmedList = ManyWords.trimEntries(wordList)
        duplicates = ManyWords.findDuplicates(trimmedList)
        if (len(duplicates) > 0 ):
            raise Exception("Set contains duplicates [" + " / ".join(duplicates) + "]")   
        self.wordList = trimmedList

    @staticmethod 
    def trimEntries(wordList):
        trimmedList = []
        for word in wordList:
            trimmedList.append(list(map(str.strip, word)))
        return trimmedList

    @staticmethod 
    def findDuplicates(wordList):
        seen = set()
        duplicates = set()
        for word in wordList:
            germanGF = word[0]
            if germanGF not in seen:
                seen.add(germanGF)
            else:
                duplicates.add(germanGF)
        return duplicates

    @staticmethod
    def isClose(actual, expected):
        return (Utils.hamming_distance(actual, expected) <= 2)

    @staticmethod
    def retype(expected):
        actual = ""
        while (actual != expected):
            actual = input("Repeat: ")
    
    @staticmethod
    def test(prompt, expected, retry=True):
        actual = input(f'{prompt} ')
        if (actual == expected):
            return True
        elif (len(actual) == 0):
            print(f'Skipping - correct answer: {expected}')
            ManyWords.retype(expected)
            return False
        elif(retry and ManyWords.isClose(actual, expected)):
            print("Close... try again")
            return ManyWords.test(prompt, expected, False)
        else:
            print(f'Nope - correct answer: {expected}')
            ManyWords.retype(expected)
            return False

    def study(self):
        trainSet = self.wordList
        trainSetLength = len(trainSet)
        trainDuration = trainSetLength * ManyWords.SECONDS_PER_WORD
        trainEndTime = datetime.now() + timedelta(seconds = trainDuration)
        doneList = []
        
        learnedPercentage = 0
        counter = 1
        remaining = (trainEndTime - datetime.now()).seconds

        print(f'\nStudy set contains {trainSetLength} words. Study time for this set is {Utils.pretty_time_delta(trainDuration)}')
        while (remaining > 0  and learnedPercentage < 100):
            print(f'\nStep {counter} - {Utils.pretty_time_delta(remaining)} remaining ({learnedPercentage}% learned)')
            
            word = random.choice(trainSet)
            word_d = dict(zip(ManyWords.FIELDS, word))
            
            correct_gf = ManyWords.test(word_d['DE GF']+':', word_d['FR GF'])
            if(correct_gf):
                randomField = random.choice(ManyWords.FIELDS[2::])
                correct_conj = ManyWords.test(ManyWords.FIELD_LABELS[randomField], word_d[randomField])
                if (correct_conj):
                    doneList.append(word)
                    trainSet.remove(word)
            
            learnedPercentage = round((len(doneList) / trainSetLength)*100)
            counter += 1
            remaining = (trainEndTime - datetime.now()).seconds

        if (learnedPercentage < 100):
            print(f'\nTime is up. You have reached a learn rate of {learnedPercentage}% for this set.')
        else:
            print(f'\nYou have completed this set! (with {Utils.pretty_time_delta(remaining)} remaining)')
        input("\nHit [ENTER] to close")


class Utils:
    @staticmethod
    def hamming_distance(chaine1, chaine2):
        return sum(c1 != c2 for c1, c2 in zip(chaine1, chaine2))
        #TODO implment a better algo to detect typos
        #hamming_distance of j'a rompu and j'ai rompu is high, should be 1

    @staticmethod
    def column(matrix, i):
        return [row[i] for row in matrix]
    
    @staticmethod
    def pretty_time_delta(seconds):
        sign_string = '-' if seconds < 0 else ''
        seconds = abs(int(seconds))
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        if days > 0:
            return '%s%dd%dh%dm%ds' % (sign_string, days, hours, minutes, seconds)
        elif hours > 0:
            return '%s%dh%dm%ds' % (sign_string, hours, minutes, seconds)
        elif minutes > 0:
            return '%s%dm%ds' % (sign_string, minutes, seconds)
        else:
            return '%s%ds' % (sign_string, seconds)


def selectSetFile():
    print("\nAvailable study sets")
    files = os.listdir(SETDIR_PATH)
    index = 0
    for f in files:
        print(f'\t{index}. {f}')
        index += 1
    selection = int(input('Select study set: '))
    setFile = SETDIR_PATH + "/" + files[selection]
    return setFile

def loadSetFile(setFile):
    wordList = []
    f = open(setFile, encoding='utf-8')
    reader = csv.reader(f)
    for row in reader:
        wordList.append(row)
    #trainList = trainList[1::]  # csv no longer contains a header row
    return wordList

def main():
    print(f'-- ManyWords {BUILD} --')
    setFile = selectSetFile()
    wordList = loadSetFile(setFile)
    m = ManyWords(wordList)
    m.study()

if __name__ == "__main__":
    main()



       
