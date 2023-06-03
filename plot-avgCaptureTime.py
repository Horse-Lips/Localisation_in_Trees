import matplotlib.pyplot as plt
import sys, ast

fName = sys.argv[1]
f = open(fName, 'r')

xAxis = [i for i in range(3, 151)]

line = f.readline()

plt.title("Probe Strategy: " + line)

for x in range(3):
    currTarget = f.readline()
    yAxis = []

    for i in range(148):
        for j in range(3):
            line = f.readline()
            if j == 1: list = ast.literal_eval(line.strip().split(": ")[1]); yAxis.append(sum(list) / len(list))

    plt.plot(xAxis, yAxis, label = currTarget)

plt.xlabel("Number of Nodes")
plt.ylabel("Capture Time")

plt.legend()
plt.show()