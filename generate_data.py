import numpy as np
import sys

numbers = np.random.uniform(low=int(sys.argv[3]), high=int(sys.argv[4]),size=(int(sys.argv[1]),2))

file = open(sys.argv[2], 'w')

for num in numbers:
	file.write(str(num[0]) + " " + str(num[1]) + "\n")