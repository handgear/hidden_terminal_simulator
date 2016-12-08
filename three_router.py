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
    total_router_num = 3
    router_range = 300
    K_limit = 4

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

class Supervisor:
    def __init__(self, total_time_slot):
        self.total_time_slot = total_time_slot
        current_time_slot = 0



#================================================================#
setting = Setting()


#make router objects
router_list = []
router_list.append(Router(300,500))
router_list.append(Router(500,500))
router_list.append(Router(700,500))

#search other routers in its range and add to .near_router[]
for i in range(setting.total_router_num):
    router_list[i].add_near_router_info(i)

#for debug
for i in range(setting.total_router_num):
    print router_list[i].near_router

#가운데는 일단 듣는 역할, 양옆 두개가 전송하려고 하는 상황
'''송신측
R=0, K=0, K_limit

RTS 보낸다(NAV도 같이 보낸다, NAV는 상대시간으로 보낸다)
5동안 기다린다.
CTS 안오면 K = K+1 (CTS 가 오긴오는데 자신것이 아니면 NAV 확인 해서 대기상태/NAV 이후 얼마나 기다릴지는 추후 구현. 기존에 기다리다가 남은 슬롯만큼만 기다리고 재전송 시도->남은 R 줄이면서 0에 도달하면 전송)
랜덤하게 정한다 (pick rand Tslot method)
다시 시도. R 을 슬롯마다 1씩 줄인다.
===
CTS받으면 다음부터 데이터 전송(60슬랏동안, 번호붙여서)
말이 전송이지 그냥 보내는 측 라우터의 DATA의 숫자 늘려주면 됨.
다 보내면 ACK 기다림.(현 구현에서는 다음 슬롯에 바로 도착하므로 확인처리(전체 value 초기화)만 하고 다음 전송을 준비하면 됨)
'''

'''수신측
RTS신호가 2개 잡히면 충돌이므로 무시 =>near_router 의 RTS 상태를 확인한다.
(보내는 측의 router RTS = [수신측 라우터 번호, NAV]) NAV=62
하나만 잡히면 해당 RTS에 CTS보내준다.
(받는 측 라우터의 CTS = [수신측 라우터번호, NAV]) NAV = 61
데이터를 60슬랏동안 받으면 다음 슬랏에 ACK를 보대준다.


'''


#RTS, CTS, DATA, ACK 모두 다른 색깔 화살표로 표시하기
#캡션 달기(화살표 안에 적어도 되고) //방법 알아보기








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


ax = plt.axes()
ax.arrow(0, 0, 100, 100, head_width=20, head_length=20, width=5, fc='k', ec='k')

plt.show()





