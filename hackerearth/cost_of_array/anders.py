test = 'hackerearth/cost_of_array/test.txt'
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

print(cost[0][0],cost,sep= '\n')

