# hidden_terminal_simulator

## Install matplotlib
check here: http://matplotlib.org/users/installing.html

## Testing environment
MAC OS 10.11.6  
python 2.7.12

## Simmulate CSMA/CA with RTS/CTS
run many_router.py with routerlib.py

## Simulate CSMA/CA without RTS/CTS
run noRTS_manyrouter.py with routerlib.py

## Change setting values
change class Setting in routerlib.py  
ex)  
    TOTAL_ROUTER_NUM = 5  
    ROUTER_RANGE = 300  
    K_LIMIT = 4  
    TOTAL_TIME_SLOT = 50  
    DATA_LENGTH = 10  


## About success rate
current success rate is presenting (sended data slot)/(total time slot) in %
so it can exceed 100%  
will fix this to more reliable value
 
## How save simulation result as png file
change class Setting  
OUTPUT_PNG = True #True / False
 
