import matplotlib.pyplot as plt
import numpy as np


colours = ["tab:orange", "tab:blue", "tab:green", "tab:red", "tab:purple", "tab:olive"]
results = open("randomTreesResults.csv", 'r').readlines()[1::]

iDict = dict()

for line in results:
    line = line.split(",")

    if line[1] not in iDict: iDict[line[1]] = {
        "colour":   int(line[0]),
        "numNodes": [],
        "cTimes":   [],
        "sTimes":   [],
        "winRatio": []
    }

    iDict[line[1]]["numNodes"].append(int(line[2]))
    iDict[line[1]]["cTimes"].append(float(line[3]))
    iDict[line[1]]["sTimes"].append(float(line[4]))
    iDict[line[1]]["winRatio"].append(line[5])

for pTypes in iDict:
    pDict = iDict[pTypes]
    
    numNodes = np.array(pDict["numNodes"])
    order = np.argsort(numNodes)
    
    pDict["numNodes"] = numNodes[order]
    pDict["cTimes"]   = np.array(pDict["cTimes"])[order]
    pDict["sTimes"]   = np.array(pDict["sTimes"])[order]
    pDict["winRatio"] = np.array(pDict["winRatio"])[order]

plt.figure()

for pTypes in iDict:
    plt.scatter(iDict[pTypes]["numNodes"], iDict[pTypes]["cTimes"], label = pTypes)
    plt.plot(iDict[pTypes]["numNodes"], iDict[pTypes]["cTimes"])

plt.xlabel("Num Nodes in Tree")
plt.ylabel("Avg Capture Time (Rounds)")

plt.legend()


plt.figure()

for pTypes in iDict:
    plt.scatter(iDict[pTypes]["numNodes"], iDict[pTypes]["sTimes"], label = pTypes)
    plt.plot(iDict[pTypes]["numNodes"], iDict[pTypes]["sTimes"])

plt.xlabel("Num Nodes in Tree")
plt.ylabel("Avg Running Time (s)")

plt.legend()

plt.show()
