import random

filename = "../TestFiles/large2.blif"
width = 27
rowCount = 200
p1 = 0.99

with open(filename, "w") as f:
    f.write(".model GenericName")
    f.write("\n\n")

    names = []

    f.write(".inputs ")
    for x in range(0, width):
        n = "inp{}".format(x)
        names.append(n)
        f.write(n)
        if x != (width-1):
            f.write(" ")
    f.write("\n\n")

    f.write(".outputs out1")
    names.append("out1")
    f.write("\n\n")


    # Write values
    f.write(".names ")
    for name in names:
        f.write(name)
        if name != names[-1]:
            f.write(" ")

    f.write("\n")

    rows = []
    while len(rows) < rowCount:
        row = ""
        for b in range(0,width):
            if random.uniform(0,1) < p1:
                row += "1"
            else:
                row += "0"
        row += " 1"
        if row not in rows:
            rows.append(row)

    rows.sort()
    for row in rows:
        f.write(row)
        f.write("\n")

    f.write("\n")
    f.write(".end\n")
    f.write("\n")
