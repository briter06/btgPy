import numpy as np
import pickle
class Activations:
    
    
    @staticmethod
    def sigmoid(x,dev=False):
        if dev:
            return x*(1-x)
        else:
            return 1 / (1 + np.exp(-x))
        
    @staticmethod
    def tanh(x,dev=False):
        if dev:
            return 1-np.power(x,2)
        else:
            return np.tanh(x)