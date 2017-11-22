T = int(input())
for i in range(T):
    C = int(input())
    if C <= 3:
        fx = 0
    else:
        gx = int(0.5*(C-2))
        fx = int(0.5*gx*(gx+1))
    print(fx)
