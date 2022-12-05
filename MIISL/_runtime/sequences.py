import random


sequenceLength = 10
sequenceFiles = ['one', 'two', 'three', 'four']
sequenceFiles1 = ['three', 'four']
sequenceFiles2 = ['one', 'four']
sequenceFiles3 = ['one', 'two']
sequenceFiles4 = ['two', 'three']
sequenceOne = ['one']
sequenceTwo = ['two']
sequenceThree = ['three']
sequenceFour = ['four']


def create_random_sequence():
    randSequence = []
    for i in range(sequenceLength):
        candidate = random.choice(sequenceFiles)
        if i>0:
            if i==(sequenceLength-1):
                while (candidate==randSequence[-1]) or (candidate==randSequence[0]):
                    candidate = random.choice(sequenceFiles)
            else:
                while candidate==randSequence[-1]:
                    candidate = random.choice(sequenceFiles)
        randSequence.append(candidate)		
    return randSequence


# hard coded 10 element w/rules (ascending from 1-4)
def createSequence1():
    sequence = []
    for i in range(sequenceLength):
        #candidate = random.choice(sequenceOne)
        if i==0:
            candidate = random.choice(sequenceOne)
        elif i==1:
            candidate = random.choice(sequenceFiles1)
        elif i ==2:
            candidate = random.choice(sequenceTwo)
        elif i==3:
            candidate = random.choice(sequenceFiles2)
        elif i==4:
            candidate = random.choice(sequenceThree)
        elif i==5:
            candidate = random.choice(sequenceFiles3)
        elif i==6:
            candidate = random.choice(sequenceFour)
        elif i==7:
            candidate = random.choice(sequenceFiles4)
        elif i==8:
            candidate = random.choice(sequenceOne)
        elif i==9:
            candidate = random.choice(sequenceFiles1)
        sequence.append(candidate)		
    return sequence


# diff order ascending
def createSequence2():
    sequence = []
    for i in range(sequenceLength):
        #candidate = random.choice(sequenceOne)
        if i==0:
            candidate = random.choice(sequenceTwo)
        elif i==1:
            candidate = random.choice(sequenceFiles2)
        elif i ==2:
            candidate = random.choice(sequenceThree)
        elif i==3:
            candidate = random.choice(sequenceFiles3)
        elif i==4:
            candidate = random.choice(sequenceFour)
        elif i==5:
            candidate = random.choice(sequenceFiles4)
        elif i==6:
            candidate = random.choice(sequenceOne)
        elif i==7:
            candidate = random.choice(sequenceFiles1)
        elif i==8:
            candidate = random.choice(sequenceTwo)
        elif i==9:
            candidate = random.choice(sequenceFiles2)
        sequence.append(candidate)		
    return sequence


# descending 4-1
def createSequence3():
    sequence = []
    for i in range(sequenceLength):
        #candidate = random.choice(sequenceOne)
        if i==0:
            candidate = random.choice(sequenceFour)
        elif i==1:
            candidate = random.choice(sequenceFiles3)
        elif i ==2:
            candidate = random.choice(sequenceThree)
        elif i==3:
            candidate = random.choice(sequenceFiles2)
        elif i==4:
            candidate = random.choice(sequenceTwo)
        elif i==5:
            candidate = random.choice(sequenceFiles1)
        elif i==6:
            candidate = random.choice(sequenceOne)
        elif i==7:
            candidate = random.choice(sequenceFiles4)
        elif i==8:
            candidate = random.choice(sequenceFour)
        elif i==9:
            candidate = random.choice(sequenceFiles3)
        sequence.append(candidate)		
    return sequence


# descending diff order
def createSequence4():
    sequence = []
    for i in range(sequenceLength):
        #candidate = random.choice(sequenceOne)
        if i==0:
            candidate = random.choice(sequenceThree)
        elif i==1:
            candidate = random.choice(sequenceFiles2)
        elif i ==2:
            candidate = random.choice(sequenceTwo)
        elif i==3:
            candidate = random.choice(sequenceFiles1)
        elif i==4:
            candidate = random.choice(sequenceOne)
        elif i==5:
            candidate = random.choice(sequenceFiles4)
        elif i==6:
            candidate = random.choice(sequenceFour)
        elif i==7:
            candidate = random.choice(sequenceFiles3)
        elif i==8:
            candidate = random.choice(sequenceThree)
        elif i==9:
            candidate = random.choice(sequenceFiles2)
        sequence.append(candidate)		
    return sequence


def create_repeating_sequence():
    dice = random.randint(1, 4)
    if dice == 1:
        return createSequence1()
    elif dice == 2:
        return createSequence2()
    elif dice == 3:
        return createSequence3()
    elif dice == 4:
        return createSequence4()
