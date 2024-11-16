import math

def combo(n, r):
	return math.factorial(n)/(math.factorial(r)*math.factorial(n-r))

solution = 0

for i in range(11):
	solution += combo(11, 11-i)

print(solution)