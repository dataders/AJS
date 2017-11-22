chef = 'codechef/TRISQ_test.txt'
lines = [int(line.rstrip('\n')) for line in open(chef)]

print(lines)

T = lines[0]
C = lines[1:]
print(T,C)

from math import fmod
AnsList = []

for i in range(T):
    tmp = (C[i]**2)/2
    ans = fmod(tmp, 4)
    AnsList.append(ans)

print(AnsList)
