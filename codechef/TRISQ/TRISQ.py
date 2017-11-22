chef = 'codechef/TRISQ_test.txt'
lines = [int(line.rstrip('\n')) for line in open(chef)]

T = lines[0]
C = lines[1:]

AnsList = []

for i in range(T):
    if C[i] <= 3:
        fx = 0
    else:
        gx = int(0.5*(C[i]-2))
        fx = int(0.5*gx*(gx+1))
    AnsList.append(fx)

for i in AnsList:
    print(i)