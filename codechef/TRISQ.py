chef = 'codechef/TRISQ_test.txt'

lines = [int(line.rstrip('\n')) for line in open(chef)]
print(lines)

T = lines[0]
C = lines[1:]
print(T,C)