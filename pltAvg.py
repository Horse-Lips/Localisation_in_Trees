import matplotlib.pyplot as plt
import sys, os


labels    = ["bLeft", "bRight", "Seager", "tLeft", "tRight"]
results   = []
positions = [0, 1, 2, 3, 4, .25, 1.25, 2.25, 3.25, 4.25, .5, 1.5, 2.5, 3.5, 4.5]

directory = sys.argv[1]

for subdir in os.listdir(sys.argv[1]):
    for resFile in os.listdir(directory + subdir):
        currFile = open(directory + subdir + "\\" + resFile)
        results.append(float(currFile.readlines()[-2].strip().split(":")[1]))

plt.bar(positions[0:5],  results[0:5],  width = .25, align = "edge", label = "Probabilistic")
plt.bar(positions[5:10], results[5:10], width = .25, align = "edge", label = "Random")
plt.bar(positions[10::], results[10::], width = .25, align = "edge", label = "UpDown")

plt.xlabel("Strategy")
plt.ylabel("Avg Capture time (Rounds)")
plt.title(sys.argv[2] + " Graph")
plt.legend()
plt.xticks(ticks = [i + .36 for i in range(len(labels))], labels =  labels)

plt.savefig(directory + "\\avgCaptTimeGraph" + sys.argv[2] + ".png")