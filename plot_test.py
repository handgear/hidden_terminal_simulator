import random
import numpy as np
import matplotlib.pyplot as plt

class Router:
    def __init__(self):
        #do it need to avoid router in same place?
        #place router in random spot
        self.x = random.randrange(1, 1000)
        self.y = random.randrange(1, 1000)

    # def adder(self, num):
    #     self.result += num
    #     return self.result

router1 = Router()

# router_num = 3 #get by user input (later)
while True :
    router_num = input("input number of routers(1<x<1500): ");
    if router_num < 1500 and router_num > 1 :
        break

router_list = [Router() for i in range(router_num)] #make router objects

# plt.plot([1,2,3,4],'bo')
plt.axis([0, 1000, 0, 1000])
# plt.plot(router1.x, router1.y,'bo')
for i in range(router_num) :
    plt.plot(router_list[i].x, router_list[i].y,'bo')
plt.ylabel('some numbers')
plt.show()




