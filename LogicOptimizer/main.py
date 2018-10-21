from argparse import *
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

# Optimize
optimzieBLIF(blif, debug=args.showDebug)

print("")

# Export the optimized blif
write_blif(blif, args.outputFile)

if args.verifyBLIF:
    print("Verifying that optimized BLIF implements same logic...")
    mergeAllIntoTopLevel(blif)
    originalBlif = read_blif(args.inputFile, createTopLevelMerged=True, debug=args.showDebug)

    if blifs_equal(originalBlif, blif) is not True:
        print("Error, blifs not equal. The logic optimizer failed.")
    else:
        print("The logic-optimized BLIF is identical to the original when expanded!")

