import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle
from matplotlib.lines import Line2D
import math


class Setting:
    MAX_ROUTER_NUM = 1500
    MAX_ROUTER_RANGE = 100
    total_router_num = 200
    router_range = 30

class Router:
    def __init__(self):
        #do it need to avoid router in same place?
        #place router in random spot
        self.x = random.randrange(1, 1000)
        self.y = random.randrange(1, 1000)
        self.near_router = []

    def add_near_router_info(self, router_n):
        coor1 = (self.x, self.y)
        for i in range(setting.total_router_num):
            if i is not router_n:#avoid adding self information
                coor2 = (router_list[i].x, router_list[i].y)
                line = Line(coor1, coor2)
                # print line.distance() #for debug
                if line.distance() < setting.router_range:
                    #add router number and coordination which is placed in coor2
                    self.near_router.append([i,router_list[i].x, router_list[i].y])

class Line:
    def __init__(self, coor1, coor2):
        self.coor1 = coor1
        self.coor2  = coor2

    def distance(self):
        x1, y1 = self.coor1
        x2, y2 = self.coor2

        return math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1),2))

setting = Setting()

#get router number and router range
# while True :
#     setting.total_router_num = input("input number of routers(1<x<1500): ")
#     if setting.total_router_num < setting.MAX_ROUTER_NUM and setting.total_router_num > 1 :
#         setting.router_range = input("input covering range of each router(1<x<100): ")
#         if setting.router_range < setting.MAX_ROUTER_RANGE and setting.router_range > 0:
#             break


#make router objects
router_list = [Router() for i in range(setting.total_router_num)]

#search other routers in its range and add to .near_router[]
for i in range(setting.total_router_num):
    router_list[i].add_near_router_info(i)


for i in range(setting.total_router_num): #for debug
    print router_list[i].near_router


#=========================drawing section==========================#
#plot axis number
plt.axis([0, 1000, 0, 1000])

for i in range(setting.total_router_num):
    #draw router
    plt.plot(router_list[i].x, router_list[i].y,'bo')

    #draw range of routers
    #color conflicting router range as red
    if len(router_list[i].near_router) is not 0:
        circle = plt.Circle((router_list[i].x, router_list[i].y), radius=setting.router_range, alpha=0.3, fc='red')
        plt.gca().add_patch(circle)
    else:
        circle = plt.Circle((router_list[i].x, router_list[i].y), radius=setting.router_range, alpha=0.3, fc='blue')
        plt.gca().add_patch(circle)


plt.show()





