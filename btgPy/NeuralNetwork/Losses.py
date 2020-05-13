import numpy as np
import pickle
class Losses:
    
    #Derivative by the obtained
    @staticmethod
    def MSE(t,y,dev=False,suma=0,n=1,sum_b=False):
        if sum_b:
            return (1/n)*suma
        elif dev:
            return 2*(y-t)
        else:
            return np.power(y-t,2)
        
    @staticmethod
    def Crossentropy(t,y,dev=False,suma=0,n=1,sum_b=False):
        if sum_b:
            return suma
        elif dev:
            return y-t
        else:
            return -((t*np.log(y))+((1-t)*(np.log(1-y))))
    
        