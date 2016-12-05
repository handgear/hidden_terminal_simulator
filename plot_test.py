import random
import numpy as np
import matplotlib.pyplot as plt

class Router:
    def __init__(self):
        self.x = random.randrange(1, 1000)
        self.y = random.randrange(1, 1000)

    # def adder(self, num):
    #     self.result += num
    #     return self.result

router1 = Router()

# router_num = 3 #get by user input (later)
router_num = input("input number of routers(1<x<3000): ");
router_list = [Router() for i in range(router_num)]

# plt.plot([1,2,3,4],'bo')
plt.axis([0, 1000, 0, 1000])
# plt.plot(router1.x, router1.y,'bo')
for i in range(router_num):
    plt.plot(router_list[i].x, router_list[i].y,'bo')
plt.ylabel('some numbers')
plt.show()





