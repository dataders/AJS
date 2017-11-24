from operator import itemgetter

def readInput(testNum):
    test = 'hackerearth/cost_of_array/test{}.txt'.format(str(testNum))
    lines = [line.rstrip('\n') for line in open(test)]
    # from sys import stdin
    # lines = [int(line.rstrip('\n')) for line in stdin]

    # define variables
    N = int(lines[0])
    A = [int(x) for x in lines[1].split()]
    B = [int(x) for x in lines[2].split()]
    M = int(lines[3])
    the_rest = lines[4:]

    cost = [[0 for x in range(N)] for y in range(N)]
    for i in range(len(the_rest)):
        cost[i] = [int(x) for x in the_rest[i].split()]
    return A,B,N,cost

A, B, N, cost = readInput(2)

A_rank = [t[0] for t in sorted(enumerate(A),
                                key=itemgetter(1),
                                reverse=True)]
B_rank = [t[0] for t in sorted(enumerate(B),
                                key=itemgetter(1),
                                reverse=True)]

print("A:", A,
    "A rank", A_rank,
    sep='\n')
print("B:", B,
    "B rank", B_rank,
    sep='\n')
# print("cost matrix:", cost, sep='\n')


x = A_rank.index(3)
y = A_rank.index(0)
print(x,y, sep=' ')

A_2 = A
A_2[x], A_2[y] = A_2[y], A_2[x]
print(A_2)