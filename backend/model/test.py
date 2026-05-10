class Parameter:
    
    def __init__(self,input = None,output = None,weight = None,lr = None):

        self.input = input
        self.output = output
        self.weight = weight
        self.lr = lr            #learning rate


def prepare() -> Parameter:

    p  = Parameter()

    p.input = [[0,0],[0,1],[1,0],[1,1]]
    p.output = [0,0,0,1]
    p.weight  = [0.5,0,5]
    p.lr = 0.02

    return p


def train(p : Parameter) ->:
