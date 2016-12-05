import matplotlib
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle
import numpy as np
from matplotlib.lines import Line2D

# (modified from one of the matplotlib gallery examples)
resolution = 50 # the number of vertices
N = 50
Na = 25
Nb = 10
x        = np.random.random(N)
y       = np.random.random(N)
radii   = 0.1*np.random.random(30)


patches = []

for x1,y1,r in zip(x, y, radii):
     circle = Circle((x1,y1), r)
     patches.append(circle)



fig = plt.figure()
ax = fig.add_subplot(111)

colors = 100*np.random.random(N)
p = PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=0.4, label= "Cat 1", facecolor="red")


ax.add_collection(p)


circ1 = Line2D([0], [0], linestyle="none", marker="o", alpha=0.4, markersize=10, markerfacecolor="red")


plt.legend([circ1] , "Cat 1",numpoints=1, loc="best")

plt.show()
