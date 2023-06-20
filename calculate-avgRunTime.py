import sys, ast
from math import inf

fName = sys.argv[1]
f     = open(fName, 'r')

line = f.readline()

mini  = [inf, inf, inf]
maxi  = [0, 0, 0]
times = []

for x in range(3):
    line  = f.readline()
    
    time  = 0
    total = 0
    
    for i in range(148):
        for j in range(3):
            line = f.readline()
            
            if j == 2:
                line = ast.literal_eval(line.strip().split(": ")[1])
                
                if min(line) > 0 and min(line) < mini[x]: mini[x] = min(line)
                if max(line) > maxi[x]:                   maxi[x] = max(line)
                time += sum(line)
                total += len(line)

    times.append(time / total)
    
print("Min:",  mini)
print("Max:",  maxi)
print("Mean:", times)