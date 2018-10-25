import sys
import os
import subprocess

def runTestWithBlifAtPath(path):
    filename = (path.split(".")[-2]).split("/")[-1]

    with open("../TestOut/{}.txt".format(filename), "w") as f:
        testProcess = subprocess.Popen(["python", "main.py", "-t", "-v", "-i", path, "-o", "../TestOut/{}Out.blif".format(filename)],
                                stdout=f)#subprocess.PIPE
        testProcess.wait()
        output, error = testProcess.communicate()

    with open("../TestOut/{}.txt".format(filename), "r") as f:
        for line in f:
            if "The logic-optimized BLIF is identical to the original when expanded!" in line:
                return True

    return False

print("Running all tests.")
print("All test results go into the \"TestOut\" folder.")
print("Each optimized BLIF file has the suffix \"Out.blif\"")
print("Console output from each test is \"<TestBlifName>.txt\"")
print("")

testFiles = os.listdir("../TestFiles")
testFiles.sort()

for testFile in testFiles:
    if testFile.endswith(".v") or testFile.startswith("."):
        continue

    testFilePath = "../TestFiles/" + testFile

    print("Optimizing BLIF file: {}".format(testFilePath))
    passed = runTestWithBlifAtPath(testFilePath)

    if passed:
        print("Success.")
    else:
        print("Failed...")


print("")
print("Done.")