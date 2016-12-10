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
    DATA_LENGTH = 2

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
        self.state = '' #state info for display
        #'RTS', 'CTS', 'DATA', 'ACK', 'WAIT'
        self.ctrl_data = {'RTS': -1, 'CTS': -1, 'DATA': 0, 'ACK': -1}
        #RTS = router number of DATA receiver
        #CTS = router number of DATA sender
        #DATA = datanumber to send (60~0)
        #ACK = router number of DATA sender
        self.backoff_data = {'R': 0, 'K': 0}

        self.receiver = [] #when this router is sender, save info
        self.sender = [] #when this router is receiver, save info
        self.time_to_send = {'RTS': 0, 'CTS': -1, 'DATA': -1, 'ACK': -1} #number of timeslot to send message
        self.time_out = {'CTS': 5, 'ACK': 5}

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
        self.backoff_data['R'] = random.randrange(0,math.pow(2,self.K))

    def set_RTS_time(self):
        supervisor = Supervisor()
        self.time_to_send['RTS'] = supervisor.current_time_slot + self.backoff_data['R']

    def initialize_sender(self):
        self.state = ''
        self.ctrl_data = {'RTS': -1, 'CTS': -1, 'DATA': 0, 'ACK': -1}
        self.backoff_data = {'R': 0, 'K': 0}
        self.sender = []
        self.time_to_send = {'RTS': 0, 'CTS': 0, 'DATA': -1, 'ACK': -1}
        self.time_out = {'CTS': 5, 'ACK': 5}

    def initialize_receiver(self):
        self.state = 'WAIT'
        self.ctrl_data = {'RTS': -1, 'CTS': -1, 'DATA': 0, 'ACK': -1}
        self.receiver = []
        self.time_to_send = {'RTS': 0, 'CTS': 0, 'DATA': -1, 'ACK': -1}
        self.time_out = {'CTS': 5, 'ACK': 5}


class Supervisor:
    def __init__(self):
        self.current_time_slot = 0
        # self.divided_time_slot = 0 #divide one time slot to two(0/1)
        # #0 for setting flags and data
        # #1 for setting time

