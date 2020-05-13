import numpy as np
import random
class Layer:
    
    def __init__(self,n=0,n_neurons=1, function=None):
        self.n = 0
        self.x = []
        self.n_neurons = n_neurons
        self.weights = []
        self.biases = []
        self.function = function
        
    def createMatrix(self,prev_n_neurons,initial_w,initial_b):
        for z in range(self.n_neurons):
            aux = []
            for i in range(prev_n_neurons):
                aux.append(random.uniform(0, 1))
            self.weights.append(aux)
            self.biases.append([random.uniform(0, 1)])
        self.weights = np.array(self.weights)
        self.biases = np.array(self.biases)
            
        
                
    def activate(self,prev_x):
            res = np.dot(self.weights,prev_x)
            self.x = res+self.biases
            self.x = self.function(self.x)
                
        