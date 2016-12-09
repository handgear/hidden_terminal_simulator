import math
from math import atan2, degrees, pi
import random

class Line:
    def __init__(self, coor1, coor2):
        self.coor1 = coor1
        self.coor2  = coor2

    def distance(self):
        x1, y1 = self.coor1
        x2, y2 = self.coor2

        return math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1),2))

    def angle(self):
        x1, y1 = self.coor1
        x2, y2 = self.coor2
        dx = x2 - x1
        dy = y2 - y1
        rads = atan2(dy,dx)
        return degrees(rads)

class Setting:
    MAX_ROUTER_NUM = 1500
    MAX_ROUTER_RANGE = 100
    TOTAL_ROUTER_NUM = 3
    ROUTER_RANGE = 300
    K_LIMIT = 4
    TOTAL_TIME_SLOT = 1

class Router:
    def __init__(self):
        #do it need to avoid router in same place?
        #place router in random spot
        self.x = random.randrange(1, 1000)
        self.y = random.randrange(1, 1000)
        self.near_router = []

    def __init__(self, x, y):
        #place router in position x,y
        self.x = x
        self.y = y
        self.near_router = []
        self.R = 0
        self.K = 0
        self.RTS = [] #[router number of DATA receiver , NAV]
        self.CTS = [] #[router number of DATA sender , NAV]
        self.ACK = [] #[router number]
        self.receiver = [] #when this router is sender, save info
        self.sender = [] #when this router is receiver, save info

    def add_near_router_info(self, router_list, router_num):
        setting = Setting()
        coor1 = (self.x, self.y)
        for i in range(setting.TOTAL_ROUTER_NUM):
            if i is not router_num:#avoid adding self information
                coor2 = (router_list[i].x, router_list[i].y)
                line = Line(coor1, coor2)
                # print line.distance() #for debug
                if line.distance() < setting.ROUTER_RANGE:
                    #add router number and coordination which is placed in coor2
                    self.near_router.append([i,router_list[i].x, router_list[i].y])

    def pick_rand_reciver(self):
        if len(self.near_router) is not 0:
            temp = random.randrange(0, len(self.near_router))
            self.receiver.append(self.near_router[temp])

    def set_R(self):
        #set R with random number between 0 and 2^K-1
        self.R = random.randrange(0,math.pow(2,self.K))





class Supervisor:
    def __init__(self):
        self.current_time_slot = 0

