import sys
import fileinput

lines = []
for line in fileinput.input():
    lines.append(line.strip())

#print lines

for line in lines:
    if line.startswith('Operation'):
        print line
    elif line.startswith('-'):
        pass
    else:
        cols = line.split(':')
        rowname = cols[0].strip()
        rowname.replace(' ', '.')
        values = cols[1].split()
        newline = [rowname] + values 
        print ' '.join(newline)

    




