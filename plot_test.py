import random
import numpy as np
import matplotlib.pyplot as plt
class Setting:
    MAX_ROUTER_NUM = 1500
    MAX_ROUTER_RANGE = 100
    router_num = 20
    router_range = 3

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
setting = Setting()


# router_num = 3 #get by user input (later)
while True :
    router_num = input("input number of routers(1<x<1500): ");
    if router_num < 1500 and router_num > 1 :
        break
#make router objects
router_list = [Router() for i in range(setting.router_num)]


plt.axis([0, 1000, 0, 1000])
# plt.plot(router1.x, router1.y,'bo')
for i in range(router_num) :
    plt.plot(router_list[i].x, router_list[i].y,'bo')
plt.ylabel('some numbers')
plt.show()





