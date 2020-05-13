import math
from scipy import stats
from btgPy.Testing.TailRes import TailRes

class HypoTest:
    
    def t_score_single_population(self,x=0,mu=0,s=1,n=1):
        return (x-mu)/(s/math.sqrt(n))
    def t_score_two_population(self,x1=0,mu1=0,s1=1,n1=1,x2=0,mu2=0,s2=1,n2=1):
        return ((x1-x2)-(mu1-mu2))/(math.sqrt((math.pow(s1,2)/n1)+(math.pow(s2,2)/n2)))
    
    def testLeft(self,two_populations=False,alpha = 0.05,x1=0,mu1=0,s1=1,n1=1,x2=0,mu2=0,s2=1,n2=1):
        t_score = 0
        op = ""
        if two_populations:
            t_score = self.t_score_two_population(x1=x1,mu1=mu1,s1=s1,n1=n1,x2=x2,mu2=mu2,s2=s2,n2=n2)
            op = "x1 < x2"
        else:
            t_score = self.t_score_single_population(x=x1,mu=mu1,s=s1,n=n1)
            op = "x < mu"
        p_value = stats.norm.cdf(t_score)
        t_critical = stats.norm.ppf(alpha)
        hypothesis = False
        if p_value<=alpha:
            hypothesis = True
        tail_r = TailRes(op=op,tail="L",t_score=t_score,alpha=alpha,t_critical=t_critical,p_value=p_value,hypothesis=hypothesis)
        return tail_r
    
    def testRight(self,two_populations=False,alpha = 0.05,x1=0,mu1=0,s1=1,n1=1,x2=0,mu2=0,s2=1,n2=1):
        t_score = 0
        op = ""
        if two_populations:
            t_score = self.t_score_two_population(x1=x1,mu1=mu1,s1=s1,n1=n1,x2=x2,mu2=mu2,s2=s2,n2=n2)
            op = "x1 > x2"
        else:
            t_score = self.t_score_single_population(x=x1,mu=mu1,s=s1,n=n1)
            op = "x > mu"
        p_value = 1 - stats.norm.cdf(t_score)
        t_critical = stats.norm.ppf(1-alpha)
        hypothesis = False
        if p_value<=alpha:
            hypothesis = True
        tail_r = TailRes(op=op,tail="R",t_score=t_score,alpha=alpha,t_critical=t_critical,p_value=p_value,hypothesis=hypothesis)
        return tail_r
    
    def test(self,op="",two_populations=False,alpha = 0.05,x1=0,mu1=0,s1=1,n1=1,x2=0,mu2=0,s2=1,n2=1):
        dic = {}
        if op=="=":
            dic["L"] = self.testLeft(two_populations=two_populations,alpha=alpha/2,x1=x1,mu1=mu1,s1=s1,n1=n1,x2=x2,mu2=mu2,s2=s2,n2=n2)
            dic["R"] = self.testRight(two_populations=two_populations,alpha=alpha/2,x1=x1,mu1=mu1,s1=s1,n1=n1,x2=x2,mu2=mu2,s2=s2,n2=n2)
            dic["H"] = not dic["L"].hypothesis and not dic["R"].hypothesis
        elif op==">":
            dic["R"] = self.testRight(two_populations=two_populations,alpha=alpha,x1=x1,mu1=mu1,s1=s1,n1=n1,x2=x2,mu2=mu2,s2=s2,n2=n2)
        elif op=="<":
            dic["L"] = self.testLeft(two_populations=two_populations,alpha=alpha,x1=x1,mu1=mu1,s1=s1,n1=n1,x2=x2,mu2=mu2,s2=s2,n2=n2)
        else:
            dic["L"] = self.testLeft(two_populations=two_populations,alpha=alpha/2,x1=x1,mu1=mu1,s1=s1,n1=n1,x2=x2,mu2=mu2,s2=s2,n2=n2)
            dic["R"] = self.testRight(two_populations=two_populations,alpha=alpha/2,x1=x1,mu1=mu1,s1=s1,n1=n1,x2=x2,mu2=mu2,s2=s2,n2=n2)
        return dic
    
    
