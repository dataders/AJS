from sys import stdin
lines = [int(line.rstrip('\n')) for line in stdin]

T = lines[0]
C = lines[1:]

for i in range(T):
    if C[i] <= 3:
        fx = 0
    else:
        gx = int(0.5*(C[i]-2))
        fx = int(0.5*gx*(gx+1))
    print(fx)
