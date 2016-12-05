import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle
from matplotlib.lines import Line2D


class Setting:
    MAX_ROUTER_NUM = 1500
    MAX_ROUTER_RANGE = 100
    router_num = 20
    router_range = 30

class Router:
    def __init__(self):
        #do it need to avoid router in same place?
        #place router in random spot
        self.x = random.randrange(1, 1000)
        self.y = random.randrange(1, 1000)

    # def adder(self, num):
    #     self.result += num
    #     return self.result

setting = Setting()

#get router number and router range
# while True :
#     setting.router_num = input("input number of routers(1<x<1500): ")
#     if setting.router_num < setting.MAX_ROUTER_NUM and setting.router_num > 1 :
#         setting.router_range = input("input covering range of each router(1<x<100): ")
#         if setting.router_range < setting.MAX_ROUTER_RANGE and setting.router_range > 0:
#             break


#make router objects
router_list = [Router() for i in range(setting.router_num)]


plt.axis([0, 1000, 0, 1000])

for i in range(setting.router_num) :
    plt.plot(router_list[i].x, router_list[i].y,'bo') #draw router
    circle = plt.Circle((router_list[i].x, router_list[i].y), radius=setting.router_range, alpha=0.3, fc='blue')
    plt.gca().add_patch(circle)


plt.show()





