from btgPy.NeuralNetwork.Layer import Layer
from sklearn.preprocessing import normalize
from btgPy.NeuralNetwork.Activations import Activations
from btgPy.NeuralNetwork.Losses import Losses
import numpy as np
import pickle

class MultiLayerPerceptron:
    
    def __init__(self,initial_w = 0.5,initial_b = 0.5,learning_rate=0.5,momentum=0.9,loss_function=Losses.MSE):
        self.layers = []
        self.initial_weight = initial_w
        self.initial_bias = initial_b
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.loss_function = loss_function
    
    def addLayer(self,n_neurons=1,function=Activations.sigmoid):
        tamanio = len(self.layers)
        layer = Layer(n=tamanio,n_neurons=n_neurons,function=function)
        if tamanio!=0:
            layer.createMatrix(self.layers[tamanio-1].n_neurons,self.initial_weight,self.initial_bias)
        self.layers.append(layer)
    
    def fit(self,inputs,outputs, epochs=100,printing=False,times_stop=100):
        times = 0
        min_error = -1
        for x in range(epochs):
            suma = 0
            for inp in range(len(inputs)):
                i = np.transpose([np.array(inputs[inp])])
                first_layer = self.layers[0]
                first_layer.x = i
                self.feedForward()
                last_layer = self.layers[len(self.layers)-1]
                n_ne = last_layer.n_neurons
                
                out = int(outputs[inp])
                target = np.array([0]*n_ne)
                target[out] = 1
                obtained = last_layer.x.flatten()
                #LossFunction
                error = self.loss_function(target,obtained,dev=True)
                e_suma = self.loss_function(target,obtained)
                suma+=np.sum(e_suma)
                self.backpropagation(error)
            m_error = self.loss_function(target,obtained,suma=suma,n=len(inputs),sum_b=True)
            m_error = np.abs(m_error)
            if min_error<0:
                min_error = m_error
            else:
                if m_error>=min_error:
                    times+=1
                else:
                    times = 0
            if times==times_stop:
                break
            if printing:
                print("Finished Epoch "+str(x+1))
        
        
    def evaluate(self,inputs,outputs):
        pred = self.predict(inputs)
        suma = 0
        for z in range(len(pred)):
            if pred[z]==outputs[z]:
                suma+=1
        accuracy = suma/len(pred)
        return accuracy
                
                
    def predict(self,inputs):
        prediction = []
        for inp in range(len(inputs)):
                i = np.transpose([np.array(inputs[inp])])
                first_layer = self.layers[0]
                first_layer.x = i
                self.feedForward()
                last_layer = self.layers[len(self.layers)-1]
                pred = last_layer.x.flatten()
                prediction.append(np.argmax(pred))
        prediction = np.array(prediction)
        return prediction
                
        
    
    def feedForward(self):
        for n_layer in range(1,len(self.layers)):
            prev_l = self.layers[n_layer-1]
            layer = self.layers[n_layer]
            layer.activate(prev_l.x)
    def backpropagation(self,error):
        err = error
        for n_layer in reversed(range(1,len(self.layers))):
            prev_l = self.layers[n_layer-1]
            layer = self.layers[n_layer]
            deriv = layer.function(layer.x,dev=True).flatten()
            deltaB = np.array([self.learning_rate*(err*deriv)])
            deltaW = np.dot(prev_l.x,deltaB)
            deltaW = np.transpose(deltaW)
            deltaB = np.transpose(deltaB)
            
            weights_before = np.copy(layer.weights)
        
            
            layer.weights = layer.weights-deltaW
            layer.biases = layer.biases-deltaB
            
            normed_matrix = normalize(weights_before, axis=1, norm='l1')
            err = np.dot(err,normed_matrix)
            
    def export(self):
        txt = pickle.dumps(self)
        return txt
        
    def load(self,obj):
        temp_ob = pickle.loads(obj)
        return temp_ob
