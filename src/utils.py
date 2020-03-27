
import random
import math


def exponencial(x):
    r = random.random()
    s = ( -1 / x ) * ( math.log(r , math.e ) )
    return s


def normal(mu, sigma):
    #x = 0
    #while True :
    #    y = exponencial(1)
    #    u = random.random()
    #    c = math.exp((-( y - 1)**2)/2)
        #c = math.fabs(c)
    #    if u <= c:
    #        x = mu + sigma * y
    #        break
    #return x
    
    a = random.random()
    b = random.random()
    c = math.sqrt( -2 * math.log( a , math.e ) ) * math.cos( 2 * math.pi * b )
    return math.sqrt( sigma ) * math.fabs(c) + mu
    
    #return random.normalvariate(mu, sigma)

for x in range(10):
    a = exponencial(8) * 60
    b = exponencial(8*60)
    c = exponencial(15)
    print((a,b,c))

