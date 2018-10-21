from TruthTable import *

class Minterm:
    def __init__(self, row=None):
        if row is not None:
            self.row = row
            self.implements = []
            self.implements.append(0xFFFFFFFF & int("".join(row), 2) )
        else:
            self.implements = []
            self.row = []

    def star(self, m1):
        row0 = self.row
        row1 = m1.row

        diff = 0
        new = []
        for i, b0 in enumerate(row0):
            b1 = row1[i]
            if b0 != b1:
                diff += 1
                if diff > 1:
                    return None
                new.append("-")
            else:
                new.append(b0)

        if diff == 0:
            return None

        m = Minterm()
        m.row = new
        m.implements.extend(self.implements)
        m.implements.extend(m1.implements)
        m.implements.sort()

        return m

    #   Counts the number of 1's in a minterm
    def countOnes(self):
        count = 0
        for m in self.row:
            if m is "1":
                count += 1
        return count

    def __eq__(self, other):
        return self.row == other.row

    def __str__(self):
        return "Term {} covers {}".format(self.row, self.implements)

    @staticmethod
    def toMintemrs(rows):
        out = []
        for row in rows:
            out.append(Minterm(row))

        return out

    @staticmethod
    def organizeByNumberOfOnes(arrayOfMinterms):
        if arrayOfMinterms is None or len(arrayOfMinterms) == 0:
            raise Exception("organizeByNumberOfOnes - arrayOfMinterms is None or empty")

        # How many bits are we working with?
        bits = len(arrayOfMinterms[0].row)
        # Make a list to hold each group of minterms
        currentNumberOfOnes = 0
        maxNumberOfOnes = (max(arrayOfMinterms, key=lambda m: m.countOnes())).countOnes()
        mintermsByNumberOfOnes = []
        # Pre allocate lists so I don't get out of bounds errors
        for x in range(0, maxNumberOfOnes + 1):
            mintermsByNumberOfOnes.append([])

        # Populate the "table"
        for minterm in arrayOfMinterms:
            c = minterm.countOnes()
            mintermsByNumberOfOnes[c].append(minterm)

        return mintermsByNumberOfOnes
    @staticmethod
    def getRowsFromMinterms(minterms):
        rows = []
        for m in minterms:
            rows.append([m.row, "1"])
        return rows

def optimzieBLIF(blif, debug=False):
    # Clear the old tt rows
    blif.ttLookup = {}

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
            if debug:
                print("Tabulating {} rows.".format(len(currentBatch)))
            tabulated = Minterm.organizeByNumberOfOnes(currentBatch)

            if debug:
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

                nextGroup = tabulated[i + 1]
                # Compare the current group with the next group to find
                #  pairs that can merge and move on to the next round.
                for lesserTerm in group:
                    for greaterTerm in nextGroup:
                        possibleNext = lesserTerm.star(greaterTerm)
                        # print("{} * {} is {}".format(lesserTerm, greaterTerm, possibleNext))
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
                # print("{} leftover in group {}".format(len(group), tabulated.index(group)))
                for minterm in group:
                    # print("Adding leftover term: {}".format(minterm))
                    primeImplicants.append(minterm)
            if debug:
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

        if debug:
            print("Coverage map:")
            coverageMap = {}
            for prime in primeImplicants:
                for i in prime.implements:
                    if i not in coverageMap:
                        coverageMap[i] = []
                    coverageMap[i].append(prime)

            for k in coverageMap:
                print("{} is covered by {}".format(k, len(coverageMap[k])))

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

        print("")
        print("Found a combination of {}/{} prime implicants that covers everything.".format(len(chosenPrimeImplicants),
                                                                                             len(primeImplicants)))

        for p in chosenPrimeImplicants:
            print(p)

        # Create a replacement truth table
        primeTT = TruthTable(tt.names, Minterm.getRowsFromMinterms(chosenPrimeImplicants), blif=blif)

        # Replace the inputs with the new prime implicants
        blif.ttLookup[tt.getOutputName()] = primeTT