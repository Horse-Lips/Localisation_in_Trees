import sys, ast

fName = sys.argv[1]
f     = open(fName, 'r')

line = f.readline()

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
                time += sum(line)
                total += len(line)

    times.append(time / total)
    
print(times)
