import random
from TruthTable import TruthTable

# Removes ".name" in front of a line
# and deletes any whitespace around all the names
def getNames(line):
    names = line.split(" ")
    newNames = []
    for n in names[1:len(names)]:
        newNames.append(n.strip())
    return newNames

class BLIF:
    def __init__(self):
        self.prefix = ""
        self.suffix = "\n.end\n"
        self.ttLookup = {}
        self.topLevelMerged = None

# Reads a blif file and returns a single, collapsed TruthTable object.
def read_blif(f, createTopLevelMerged=True, debug=0):

    # Cheap-o way to make a generic object.
    blif = BLIF()

    # Multiple .name lines can appear in a row
    #  with the following truth table line(s) applying to all
    #  of them.
    nameRows = []
    truthTableRows = []

    # Read the blif file and create truth table objects
    for line in f:
        if line.startswith(".name"):
            names = getNames(line)
            if len(names) is 1:
                continue
            nameRows.append(getNames(line))
        elif line.startswith(".model"):
            modelName = getNames(line)[0]
            blif.modelName = modelName
        elif line.startswith(".inputs"):
            blif.inputNames = getNames(line)
        elif line.startswith(".outputs"):
            blif.outputNames = getNames(line)
        elif line.startswith(".end"):
            break
        elif len(line) <= 2:
            # Blank space line or a line we don't care about

            # Process what we've accumulated
            for nameRow in nameRows:
                #print("Name row: {}".format(nameRow))
                tt = TruthTable(nameRow, truthTableRows, blif)
                blif.ttLookup[tt.getOutputName()] = tt
                #print("Added truth table: {}".format(tt))
            # Clear for next time
            nameRows = []
            truthTableRows = []
        else:
            #Truth table line
            #print("Truth table line: {}, {}".format(line, len(line)))
            ttInputs, ttOutput = line.split(" ")
            ttInputs = list(ttInputs)
            ttOutput = ttOutput.strip()
            truthTableRows.append( [ttInputs, ttOutput] )

    blif.topLevelMerged = None
    if createTopLevelMerged is True:
        # Expand the don't care cases of each truth table
        for tt in blif.ttLookup.values():
            tt.eliminateDontCares()

        # Exhaust the list of outputs (for zeros)
        for tt in blif.ttLookup.values():
            tt.exhaustOutputs()

        # Merge truth tables to make one big truth table
        blif.topLevelMerged = []
        for tt in blif.ttLookup.values():
            # Only collapse the truth tables that are at the very highest level
            # e.g. their output is a top level output
            #print("tt output name: {}".format(tt.getOutputName()))
            #print("blif outputs: {}".format(blif.outputNames))
            if tt.getOutputName() in blif.outputNames:
                print("Merging tt with output {}".format(tt.getOutputName()))
                tt.mergeChildren()
                blif.topLevelMerged.append(tt)

    # Print debug info?
    if debug == 1:
        print("")
        print("Debug:")
        print("All")
        for tt in blif.ttLookup.values():
            print(tt)
            print(tt.ttString())

        if blif.topLevelMerged is not None:
            print("Top level")
            for tt in blif.topLevelMerged:
                print(tt)
                print(tt.ttString())
    return blif

def write_blif(blif, f):
    f.write(".model ")
    f.write(blif.modelName)
    f.write("\n")

    # Write inputs
    f.write(".inputs ")
    last = blif.outputNames[len(blif.outputNames) - 1]
    for name in blif.inputNames:
        f.write(name)
        if name != last:
            f.write(" ")

    f.write("\n")

    # Write outputs
    f.write(".outputs ")
    last = blif.outputNames[len(blif.outputNames) - 1]
    for name in blif.outputNames:
        f.write(name)
        if name != last:
            f.write(" ")

    f.write("\n\n")

    # Write truth tables.
    toExport = None
    if blif.topLevelMerged is not None:
        toExport = blif.topLevelMerged
    else:
        toExport = blif.ttLookup.values()

    for tt in toExport:
        f.write(".names ")
        f.write(tt.ttString(includeZeroOutputs=False))
        f.write("\n")

    f.write(".end\n")

def blifs_equal(blif0, blif1):
    if len(blif0.ttLookup.values()) != len(blif1.ttLookup.values()):
        return False

    for key in blif0.ttLookup.keys():
        if key not in blif1.ttLookup:
            return False
        if blif0.ttLookup[key] != blif1.ttLookup[key]:
            return False

    return True

# Should we test the BLIF importer/exporter?
def runBLIFTests():
    for bits in range(2, 28):
        mintermCount = bits * 2
        print("Testing export/import with {} bit input and {} minterms.".format(bits, mintermCount))

        originalBlif = BLIF()
        originalBlif.modelName = "Model{}Bit".format(bits)
        originalBlif.inputNames = ["inp{}".format(i) for i in range(0,bits)]
        originalBlif.outputNames = ["out1"]

        truthTableRows = []
        usedTerms = []
        m = 0
        while m < mintermCount:
            # Generate a minterm
            minterm = []
            # Get random inputs
            mintermBits = random.randrange(0, (1<<bits))

            # Skip if we did it already
            if mintermBits in usedTerms:
                continue

            # Convert each bit to a string
            for i in range(0, bits):
                if (mintermBits & (1 << i)) > 0:
                    minterm.append("1")
                else:
                    minterm.append("0")

            usedTerms.append(mintermBits)
            truthTableRows.append([minterm, "1"])
            m += 1

        names = list(originalBlif.inputNames)
        names.append(originalBlif.outputNames[0])
        tt = TruthTable(names, truthTableRows, blif=originalBlif)
        originalBlif.ttLookup[tt.getOutputName()] = tt
        #print(tt)
        #print(tt.ttString())

        print("Writing out...")
        testOutName = "./test{}minterms.blif".format(bits)
        with open(testOutName, "w") as f:
            write_blif(originalBlif, f)

        print("Reading in...")
        rereadBlif = None
        with open(testOutName, "r") as f:
            rereadBlif = read_blif(f, createTopLevelMerged=False)

        if blifs_equal(originalBlif, rereadBlif) is not True:
            print("Error, blifs not equal. The exporter/importer isn't working!")
            print("Failed with {} bits.".format(bits))
        else:
            print("Success with {} bits.".format(bits))