from math import pow

class TruthTable:
    def __init__(self, names, truthTableRows, blif=None):
        if names is not None and len(names) is 0:
            raise Exception("Error processing names line: no names!")

        self.names = names

        self.blif = blif

        self.ttInputs_ones = []
        self.ttInputs_zeros = []

        for row in truthTableRows:
            self.addTruthTableLine(row[0], row[1])

        self.ttInputs_ones.sort()
        self.ttInputs_zeros.sort()

    def addTruthTableLine(self, ttInputs, ttOutput):
        assert (len(ttOutput) == 1)
        if ttOutput is "1":
            self.ttInputs_ones.append(ttInputs)
        elif ttOutput is "0":
            self.ttInputs_zeros.append(ttInputs)

    # Replace don't cares with two equivalent statements.
    def eliminateDontCares(self):
        # Define a function we can use on both one and zero outputs
        def eliminateDCs(rows):
            currentRows = rows
            newRows = []

            while True:
                for row in currentRows:
                    if "-" in row:
                        # Replace the don't-care term with two terms.
                        idx = row.index("-")
                        c0 = list(row)
                        c0[idx] = "0"
                        c1 = list(row)
                        c1[idx] = "1"
                        # Eliminate duplicates
                        if c0 not in newRows:
                            newRows.append(c0)
                        if c1 not in newRows:
                            newRows.append(c1)
                    else:
                        # Term has no don't-cares
                        newRows.append(row)

                if currentRows == newRows:
                    break
                else:
                    currentRows = newRows
                    newRows = []
                    continue

            return newRows

        self.ttInputs_ones = eliminateDCs(self.ttInputs_ones)
        self.ttInputs_zeros = eliminateDCs(self.ttInputs_zeros)

        self.ttInputs_ones.sort()
        self.ttInputs_zeros.sort()

    # Some truth tables output to other truth tables which rely on "0"
    #  outputs. We need our truth tables to cover those.
    # This method will fill in the "0" outputs
    def exhaustOutputs(self):
        if len(self.ttInputs_ones) is 0:
            return

        width = len(self.ttInputs_ones[0])
        size = int( pow(2, len(self.ttInputs_ones[0])) )
        for x in range(0, size):
            binList = list( bin(x)[2:].zfill(width) )
            if binList not in self.ttInputs_ones:
                self.addTruthTableLine(binList, "0")

    def mergeChildren(self):
        if self.blif is None:
            raise Exception("blif cannot be None to call mergeChildren.")

        # Find child truth tables that can be merged
        for name in self.getInputNames():
            if name not in self.blif.inputNames:
                # The name isn't a top level input so it can be merged
                # Tell the truth table to merge its children before we merge it
                child = self.blif.ttLookup[name]
                child.mergeChildren()
                # Get the index of the child tt in our names
                # (Index will be the same for the input values list)
                nameIndex = self.names.index(name)
                # Remove the name (guaranteed to be unique because BLIF)
                self.names.remove(name)
                # Insert the child truth table to the name list
                # Fancy syntax will merge list inside another list
                self.names[nameIndex:nameIndex] = child.getInputNames()
                # Merge the truth table values
                # The new row will most likely become multiple new rows
                newttInputs_ones = []
                for parentRow in self.ttInputs_ones:
                    if parentRow[nameIndex] is "1":
                        for childRow in child.ttInputs_ones:
                            # Copy the parent row
                            copiedRow = list(parentRow)
                            # Delete the old, single value
                            del copiedRow[nameIndex]
                            # Insert the multiple values
                            copiedRow[nameIndex:nameIndex] = childRow
                            newttInputs_ones.append(copiedRow)
                    elif parentRow[nameIndex] is "0":
                        for childRow in child.ttInputs_zeros:
                            # Copy the parent row
                            copiedRow = list(parentRow)
                            # Delete the old, single value
                            del copiedRow[nameIndex]
                            # Insert the multiple values
                            copiedRow[nameIndex:nameIndex] = childRow
                            newttInputs_ones.append(copiedRow)
                self.ttInputs_ones = newttInputs_ones

                newttInputs_zeros = []
                for parentRow in self.ttInputs_zeros:
                    if parentRow[nameIndex] is "1":
                        for childRow in child.ttInputs_ones:
                            # Copy the parent row
                            copiedRow = list(parentRow)
                            # Delete the old, single value
                            del copiedRow[nameIndex]
                            # Insert the multiple values
                            copiedRow[nameIndex:nameIndex] = childRow
                            newttInputs_zeros.append(copiedRow)
                    elif parentRow[nameIndex] is "0":
                        for childRow in child.ttInputs_zeros:
                            # Copy the parent row
                            copiedRow = list(parentRow)
                            # Delete the old, single value
                            del copiedRow[nameIndex]
                            # Insert the multiple values
                            copiedRow[nameIndex:nameIndex] = childRow
                            newttInputs_zeros.append(copiedRow)

                self.ttInputs_zeros = newttInputs_zeros

                self.ttInputs_ones.sort()
                self.ttInputs_zeros.sort()

    def getInputNames(self):
        return self.names[0:len(self.names)-1]

    def getOutputName(self):
        return self.names[len(self.names)-1]

    def __str__(self):
        return "TruthTable {} names and {} table lines.".format(len(self.names), len(self.ttInputs_zeros) + len(self.ttInputs_ones))

    def __eq__(self, other):
        if len(self.names) != len(other.names):
            return False
        if len(self.ttInputs_ones) != len(other.ttInputs_ones):
            return False
        if len(self.ttInputs_zeros) != len(other.ttInputs_zeros):
            return False

        self.ttInputs_ones.sort()
        other.ttInputs_ones.sort()

        for i, row in enumerate(self.ttInputs_ones):
            if str(row) != str(other.ttInputs_ones[i]):
                return False

        for i, name in enumerate(self.names):
            if name != other.names[i]:
                return False

        return True

    # Get a string that describes the truth table in BLIF format
    def ttString(self, includeZeroOutputs=True):
        lines = []
        last = self.names[len(self.names)-1]
        for name in self.names:
            lines.append(name)
            if name != last:
                lines.append(" ")
        lines.append("\n")
        for row in self.ttInputs_ones:
            lines.append("".join(row))
            lines.append(" ")
            lines.append("1\n")
        if includeZeroOutputs:
            for row in self.ttInputs_zeros:
                lines.append("".join(row))
                lines.append(" ")
                lines.append("0\n")
        return "".join(lines)