


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