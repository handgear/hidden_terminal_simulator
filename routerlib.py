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
    TOTAL_ROUTER_NUM = 5
    ROUTER_RANGE = 300
    K_LIMIT = 4
    TOTAL_TIME_SLOT = 30
    DATA_LENGTH = 2

class Router:
    # def __init__(self):
    #     #do it need to avoid router in same place?
    #     #place router in random spot
    #     self.x = random.randrange(1, 1000)
    #     self.y = random.randrange(1, 1000)
    #     self.near_router = []
    #     self.state = '' #state info for display
    #     #'RTS', 'CTS', 'DATA', 'ACK', 'WAIT'
    #     self.ctrl_data = {'RTS': -1, 'CTS': -1, 'DATA': 0, 'ACK': -1}
    #     #RTS = router number of DATA receiver
    #     #CTS = router number of DATA sender
    #     #DATA = datanumber to send (60~0)
    #     #ACK = router number of DATA sender
    #     self.backoff_data = {'R': 0, 'K': 0}
    #     self.receiver = -1 #when this router is sender, save info
    #     self.sender = -1 #when this router is receiver, save info
    #     self.time_to_send = {'RTS': 0, 'CTS': -1, 'DATA': -1, 'ACK': -1} #number of timeslot to send message
    #     self.time_out = {'CTS': 2, 'ACK': 2}
    #     self.time_to_end = {'DATA': -1, 'NAV': -1}
    #     self.reset = 0 #flag 1 for sender reset, 2 for receiver reset
    #     self.sender_list = []

    def __init__(self, x=None, y=None):
        #place router in position x,y
        if x is None and y is None:
            self.x = random.randrange(1, 1000)
            self.y = random.randrange(1, 1000)
        else:
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
        self.receiver = -1 #when this router is sender, save info
        self.sender = -1 #when this router is receiver, save info
        self.time_to_send = {'RTS': 0, 'CTS': -1, 'DATA': -1, 'ACK': -1} #number of timeslot to send message
        self.time_out = {'CTS': 5, 'ACK': 5}
        self.time_to_end = {'DATA': -1}
        self.NAV = 0
        self.reset = 0 #flag 1 for sender reset, 2 for receiver reset
        self.sender_list = []

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
        self.backoff_data['R'] = random.randrange(0,math.pow(2,self.backoff_data['K']))

    def set_RTS_time(self, current_time_slot):
        self.time_to_send['RTS'] = current_time_slot + self.backoff_data['R']

    def initialize_sender(self):
        self.state = ''
        self.ctrl_data = {'RTS': -1, 'CTS': -1, 'DATA': 0, 'ACK': -1}
        self.backoff_data = {'R': 0, 'K': 0}
        self.sender = -1
        self.time_to_send = {'RTS': 0, 'CTS': -1, 'DATA': -1, 'ACK': -1}
        self.time_out = {'CTS': 5, 'ACK': 5}
        self.time_to_end = {'DATA': -1, 'NAV': -1}
        self.reset = 0
        self.NAV = 0

    def initialize_sender_without_RK(self):
        self.state = ''
        self.ctrl_data = {'RTS': -1, 'CTS': -1, 'DATA': 0, 'ACK': -1}
        self.sender = -1
        self.time_to_send = {'RTS': 0, 'CTS': -1, 'DATA': -1, 'ACK': -1}
        self.time_out = {'CTS': 5, 'ACK': 5}
        self.time_to_end = {'DATA': -1, 'NAV': -1}
        self.reset = 0

    def initialize_receiver(self):
        self.state = ''
        self.ctrl_data = {'RTS': -1, 'CTS': -1, 'DATA': 0, 'ACK': -1}
        self.receiver = -1
        self.time_to_send = {'RTS': 0, 'CTS': -1, 'DATA': -1, 'ACK': -1}
        self.time_out = {'CTS': 5, 'ACK': 5}
        self.time_to_end = {'DATA': -1, 'NAV': -1}
        self.reset = 0
        self.sender_list = []

    def is_channal_idle(self, router_list):
        near_router_sending = 0
        for j in range(len(self.near_router)):
                num = self.near_router[j][0] #router number
                # print "num: " + str(num)
                # print "router_list[num].state: " + str(router_list[num].state)
                if router_list[num].state == 'RTS' or router_list[num].state == 'CTS' or router_list[num].state == 'ACK':
                    near_router_sending = near_router_sending + 1
        # print "near_router_sending: " + str(near_router_sending)
        if near_router_sending == 0:
            return True
        else:
            return False

class Supervisor:
    def __init__(self):
        self.current_time_slot = 0
        self.transfer_success = 0.0

