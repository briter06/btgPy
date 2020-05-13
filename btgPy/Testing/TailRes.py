class TailRes:
    def __init__(self,op,tail,t_score,alpha,t_critical,p_value,hypothesis):
        self.op = op
        self.tail = tail
        self.t_score = t_score
        self.alpha = alpha
        self.t_critical = t_critical
        self.p_value = p_value
        self.hypothesis = hypothesis
        
    def __str__(self):
        txt = ""
        txt += "Tail: "+str(self.tail) + "\n"
        txt += "Test Statistic (T score): "+str(self.t_score) + "\n"
        txt += "Critical T value: "+str(self.t_critical) + "\n"
        txt += "Alpha: "+str(self.alpha) + "\n"
        txt += "P-value: "+str(self.p_value) + "\n"
        txt += "The hypothesis "+self.op+" is "+str(self.hypothesis) + "\n"
        return txt