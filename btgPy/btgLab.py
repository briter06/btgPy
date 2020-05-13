from btgPy.CHAID import Tree
import csv
import copy
import os
import numpy as np
import pandas as pd

class btgLab:
    
    def __init__(self):
        self.titles = []
        self.types = []
        self.dataset = []
        self.name = ""

    def chaid(self,indep_variables,dep_variable,merge=0.05,split_threshold=0.5,depth=1,min_parent=100,min_child=50,save_dataset=False,render=False):
        aux_variables = copy.copy(indep_variables)
        data = []
        columnas = []
        if np.size(indep_variables,axis=0) == 0:
            data = self.dataset
            columnas = self.titles
        else:
            for x in range(len(indep_variables)):
                indep_variables[x] = int(self.titles.index(indep_variables[x]))
            indep_variables.append(self.titles.index(dep_variable))
            indep_variables.sort()
            columnas = [self.titles[i] for i in indep_variables]
            data = self.dataset[:,indep_variables]
            types = [self.types[i] for i in indep_variables]
                
        df = pd.DataFrame(data)
        df.columns = columnas
        independent_variable_columns = np.delete(columnas,columnas.index(dep_variable),0)
        tree = Tree.from_pandas_df(df,
                                   dict(zip(independent_variable_columns,types)),
                                   dep_variable,
                                   alpha_merge=merge,
                                   max_depth=depth,
                                   min_parent_node_size=min_parent,
                                   min_child_node_size=min_child,
                                   split_threshold=split_threshold)
        
        if len(tree.tree_store) !=0:
            res = ""
            for x in aux_variables:
                res = res+"_"+x
            if save_dataset:
                if len(tree.tree_store) != 1:
                    partes = tree.predict_separated(data,columnas,res)
                    
                    p_datos = partes[0]
                    p_titulos = partes[1]
                    self.titles = self.titles + p_titulos
                    self.dataset = np.append(self.dataset,p_datos,axis=1)
                    self.types = self.types + (['nominal']*len(p_titulos))
            
            
                
                            
            if render:
                if not os.path.exists('CHAID_tree_images'):
                    os.makedirs('CHAID_tree_images')
                resp = "CHAID_tree_images/res"+res
                tree.render(path=resp, view=True)
                os.remove(resp)
        return tree
                
        
        
    def read(self,file):
        self.name = file
        arr = np.loadtxt(file, delimiter=",", skiprows=2)
        with open(file, encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            row = next(reader)
            self.types = row
            row2 = next(reader)
            self.titles = row2
        
        self.dataset = arr
    def readDataFrame(self,df,types,name):
        self.name = name+".csv"
        self.types = types
        self.dataset = df.values
        self.titles = df.columns.values.tolist()
        
    def export(self):
        full = np.append([self.titles],self.dataset,axis=0)
        full = np.append([self.types],full,axis=0)
        df = pd.DataFrame(full)
        if not os.path.exists('saved_csv'):
            os.makedirs('saved_csv')
        df.to_csv ('saved_csv/saved_'+self.name, index = None, header=False)
        
