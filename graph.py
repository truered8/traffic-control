<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e
from matplotlib import pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d
import numpy as np
import sys

with open(sys.argv[1], 'rb') as f:
	lines = f.readlines()
	y = [int(str(line)[32:35]) for line in lines]

y = gaussian_filter1d(y, sigma=3)

fig = plt.figure()

ax1 = fig.add_subplot(111)

ax1.set_title("Frames Waited as a Function of Episodes")    
ax1.set_xlabel('Episodes')
ax1.set_ylabel('Frames Waited')
#ax1.set(xlim=(0, len(y)), ylim=(0, 1000))

ax1.plot(y)

leg = ax1.legend()

<<<<<<< HEAD
=======
=======
from matplotlib import pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d
import numpy as np
import sys

with open(sys.argv[1], 'rb') as f:
	lines = f.readlines()
	y = [int(str(line)[32:35]) for line in lines]

y = gaussian_filter1d(y, sigma=3)

fig = plt.figure()

ax1 = fig.add_subplot(111)

ax1.set_title("Frames Waited as a Function of Episodes")    
ax1.set_xlabel('Episodes')
ax1.set_ylabel('Frames Waited')
#ax1.set(xlim=(0, len(y)), ylim=(0, 1000))

ax1.plot(y)

leg = ax1.legend()

>>>>>>> d7063b3b83a5f01b86467f8c0c906e4a4acd70b5
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e
plt.show()