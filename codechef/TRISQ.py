# from sys import stdin
# lines = [line.rstrip('\n') for line in stdin]


chef = 'codechef/TRISQ_test.txt'
lines = [int(line.rstrip('\n')) for line in open(chef)]

print(lines)

T = lines[0]
C = lines[1:]
print(T,C)

from math import fmod
t = int(input())
AnsList = []
for i in range(t):
    b = int(input())
    ans = fmod((b^2/2),4)
    AnsList.append(ans)
for i in AnsList:
    print(i)