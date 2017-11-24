dot_og = sum([A[i]*B[i] for i in range(N)])

A_new = A
A_new[0], A_new[2] = A_new[2], A_new[0]
dot_new = sum([A_new[i]*B[i] for i in range(N)])


print("dot products", dot_og, dot_new, sep='\n')