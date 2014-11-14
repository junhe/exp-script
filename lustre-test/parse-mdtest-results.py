import sys
import fileinput

def isdataline(line):
    starts = ['Directory creation', 'Directory stat', 'Directory removal', 
              'File creation', 'File stat', 'File read', 'File removal', 
              'Tree creation', 'Tree removal']
    for start in starts:
        if line.startswith(start):
            return True

    return False


lines = []
for line in fileinput.input():
    lines.append(line.strip())

print 'Operation Max  Min  Mean Std.Dev'
for line in lines:
    if isdataline(line):
        cols = line.split(':')
        rowname = cols[0].strip()
        rowname = rowname.replace(' ', '.')
        values = cols[1].split()
        newline = [rowname] + values 
        print ' '.join(newline)
    else:
        pass

    




