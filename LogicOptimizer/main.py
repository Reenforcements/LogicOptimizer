from argparse import *
import math
import random
import sys
from blif import *
from optimize import *

# Get input/output files
parser = ArgumentParser(description="LogicOpt - The better logic optimizer.")

parser.add_argument("-i", dest="inputFile", type=FileType('r'), action='store', required=True)
parser.add_argument("-o", dest="outputFile", type=FileType('w'), default="./output.blif", action='store')
parser.add_argument("-t", dest="runBLIFTests", help="Run the BLIF import/export tests.", action='store_const', default=False, const=True)
parser.add_argument("-d", dest="showDebug", help="Show debug info.", action='store_const', default=False, const=True)
parser.add_argument("-v", dest="verifyBLIF", help="Verify the optimized BLIF against the original.", action='store_const', default=False, const=True)

args = parser.parse_args()

# Should we test the BLIF importer/exporter?
if args.runBLIFTests:
    runBLIFTests()

# Optimization

# Actually read in the blif
blif = read_blif(args.inputFile, createTopLevelMerged=True, debug=args.showDebug)

for tt in blif.topLevelMerged:
    print("Performing optimization on {}".format(tt))
    print(tt.ttString())

    # Convert the rows to minterm objects
    # Minterms keep track of what outputs they cover.
    currentBatch = Minterm.toMintemrs(tt.ttInputs_ones)
    # What minterms do we need to cover?
    # Get this so we can use it later
    needToCover = []
    for m in currentBatch:
        # Each term should only have one implement at this point
        needToCover.append(m.implements[0])

    primeImplicants = []

    while True:
        if args.showDebug:
            print("Tabulating {} rows.".format(len(currentBatch)))
        tabulated = Minterm.organizeByNumberOfOnes(currentBatch)

        if args.showDebug:
            print("Current batch: ")
            for m in currentBatch:
                print(m)
            print("")

        usedTerms = []
        forNextRound = []

        # Optimize using the table method described in the book.
        for i, group in enumerate(tabulated):
            if group == tabulated[-1]:
                # Last group has nothing to merge with
                break

            nextGroup = tabulated[i+1]
            # Compare the current group with the next group to find
            #  pairs that can merge and move on to the next round.
            for lesserTerm in group:
                for greaterTerm in nextGroup:
                    possibleNext = lesserTerm.star(greaterTerm)
                    #print("{} * {} is {}".format(lesserTerm, greaterTerm, possibleNext))
                    if possibleNext is not None:
                        usedTerms.append(lesserTerm)
                        usedTerms.append(greaterTerm)
                    if possibleNext is not None and possibleNext not in forNextRound:
                        forNextRound.append(possibleNext)

        # We found a bunch of pairs, but now we need to remove them
        #  so we can find the leftover prime implicants with no matches.
        for used in usedTerms:
            if used in tabulated[used.countOnes()]:
                tabulated[used.countOnes()].remove(used)

        # Grab all the prime implicants
        for group in tabulated:
            #print("{} leftover in group {}".format(len(group), tabulated.index(group)))
            for minterm in group:
                #print("Adding leftover term: {}".format(minterm))
                primeImplicants.append(minterm)
        if args.showDebug:
            print("We found {} contestants who get to move on ({} left over as prime implicants).".format(
               len(forNextRound), len(primeImplicants)))

        if len(forNextRound) == 0:
            # We don't have any for the next round.
            break

        currentBatch = forNextRound

    # Gather our prime implicants and find minimum cover.
    print("Finding decent cover using {} prime implicants.".format(len(primeImplicants)))
    for prime in primeImplicants:
        print(prime)

    # print("Coverage map:")
    # coverageMap = {}
    # for prime in primeImplicants:
    #     for i in prime.implements:
    #         if i not in coverageMap:
    #             coverageMap[i] = []
    #         coverageMap[i].append(prime)
    #
    # for k in coverageMap:
    #     print("{} is covered by {}".format(k, len(coverageMap[k])))


    chosenPrimeImplicants = []

    # We need to make sure that we cover all the minterms in needToCover
    while len(needToCover) > 0:
        mintermNum = needToCover[0]

        # Find a prime implicant that covers this.
        for prime in primeImplicants:
            if mintermNum in prime.implements:
                chosenPrimeImplicants.append(prime)
                # Remove all the minterm numbers that this prime
                #  implicant covers
                for implement in prime.implements:
                    if implement in needToCover:
                        needToCover.remove(implement)

                mintermNum = None
                break

        if mintermNum is not None:
            raise Exception("Couldn't find a prime implicant to cover minterm {}.".format(mintermNum))


    print("Found a combination of {}/{} prime implicants that covers everything.".format(len(chosenPrimeImplicants), len(primeImplicants)))
    for p in chosenPrimeImplicants:
        print(p)


