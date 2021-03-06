import csv
import random
import hashlib
import os
import sys
from datetime import datetime, timedelta
from os.path import expanduser

BUILD = "0.5"

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

    def __init__(self, word_list):
        trimmedList = ManyWords.trimEntries(word_list)
        duplicates = ManyWords.findDuplicates(trimmedList)
        if (len(duplicates) > 0 ):
            raise ValueError("Set contains duplicates [" + " / ".join(duplicates) + "]")   
        if(len(trimmedList) == 0 ):
            raise ValueError("Set is empty") 
        self.wordList = trimmedList

    @staticmethod 
    def trimEntries(word_list):
        trimmedList = []
        line = 1
        for word in word_list:
            if (len(word) != len(ManyWords.FIELDS)): 
                raise ValueError(f'Missing field(s) in row {line} of file {str(word)}')
            trimmedList.append(list(map(str.strip, word)))
            line += 1
        return trimmedList

    @staticmethod 
    def findDuplicates(word_list):
        seen = set()
        duplicates = set()
        for word in word_list:
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
    def testWord(prompt, expected, retry=True):
        actual = input(f'{prompt} ')
        if (actual == expected):
            return True
        elif (len(actual) == 0):
            print(f'Skipping - correct answer: {expected}')
            ManyWords.retype(expected)
            return False
        elif(retry and ManyWords.isClose(actual, expected)):
            print("Close... try again")
            return ManyWords.testWord(prompt, expected, False)
        else:
            print(f'Nope - correct answer: {expected}')
            ManyWords.retype(expected)
            return False

    def study(self):
        train_set = self.wordList
        set_length = len(train_set)
        study_time = set_length * ManyWords.SECONDS_PER_WORD
        study_end = datetime.now() + timedelta(seconds = study_time)
        doneList = []
        
        print(f'\nStudy set contains {set_length} words. Study time for this set is {Utils.pretty_time_delta(study_time)}')
        learned_perc = 0
        counter = 1
        remaining_time = (study_end - datetime.now()).seconds
        while ((datetime.now() < study_end) and learned_perc < 100):
            print(f'\nStep {counter} - {Utils.pretty_time_delta(remaining_time)} remaining ({learned_perc}% learned)')
            
            word = random.choice(train_set)
            word_d = dict(zip(ManyWords.FIELDS, word))
            
            correct_gf = ManyWords.testWord(word_d['DE GF']+':', word_d['FR GF'])
            if(correct_gf):
                randomField = random.choice(ManyWords.FIELDS[2::])
                correct_conj = ManyWords.testWord(ManyWords.FIELD_LABELS[randomField], word_d[randomField])
                if (correct_conj):
                    doneList.append(word)
                    train_set.remove(word)
            
            learned_perc = round((len(doneList) / set_length)*100)
            counter += 1
            remaining_time = (study_end - datetime.now()).seconds

        if (learned_perc < 100):
            print(f'\nTime is up. You have reached a learn rate of {learned_perc}% for this set.')
        else:
            print(f'\nYou have reached 100% and completed this set!')

        #add grade equivalent calculation, (doneSet -  mistakes) / trainSet *5 +1 


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

DOCDIR = "Documents"
SETDIR = "ManyWords"

def selectSetFile():
    home  = expanduser("~")
    path = os.path.join(home, DOCDIR, SETDIR)
    print (f'\nSearching for study sets in {path}')
    
    try:
        files = os.listdir(path)
    except FileNotFoundError:
        print("\nError: Set directory not found") 
        exit()

    csv_files = [a_file for a_file in files if str.endswith(a_file,"csv")]

    if (len(csv_files) == 0 ):
        print("\nError: No study set files in set directory")
        exit()
        
    print("\nAvailable study sets")
    index = 1
    for f in csv_files:
        print(f'\t{index}. {f}')
        index += 1
    selection = int(input('Select study set: '))
    setFile = os.path.join(path, files[selection-1])
    return setFile

def loadSetFile(setFile):
    wordList = []
    f = open(setFile, encoding='utf-8')
    reader = csv.reader(f)
    for row in reader:
        wordList.append(row)
    return wordList

def main():
    print(f'--- ManyWords {BUILD} ---')
    setFile = selectSetFile()
    wordList = loadSetFile(setFile)
   
    try:
        m = ManyWords(wordList)
    except ValueError as e:
        print("Error: "+ str(e))
        exit()
    m.study()
    exit()

def exit():
    input("\nPress [ENTER] to exit")
    sys.exit(0)

if __name__ == "__main__":
    main()
