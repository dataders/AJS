chef = 'TRISQ-test.txt'
lines = [line.rstrip('\n') for line in open(chef)]
T = int(lines[0])
C = int(lines[1:])
print(T,C, sep='\n')