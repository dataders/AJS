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

swaps = [(1,2)
        ,(3,4)]

print("A:",A,"B:", B, sep='\n')
print("cost matrix:", cost,
        "swaps", swaps, sep='\n')