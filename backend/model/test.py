import pandas as pd

class Parameter:
    
    def __init__(self,input = None,output = None,weight = None,lr = None,bia = None):

        self.input = input
        self.output = output
        self.weight = weight
        self.lr = lr     
        self.bia = bia       #learning rate


def prepare() -> Parameter:

    p  = Parameter()

    p.input = [[0,0],[0,1],[1,0],[1,1]]
    p.output = [0,0,0,1]
    p.weight  = [0.5,0,5]
    p.lr = 0.02
    p.bia =0
 
    return p


def train(p : Parameter,epoch : int) -> None:
    
    for x in range(0,epoch):
        for y in range(0,len(p.input)):

            result = (p.input[y][0] * p.weight[0]) + (p.input[y][1] * p.weight[1]) + p.bia

            if result > 0:

                answer = 1
            else:
                answer  = 0

            error = p.output[y] - answer 

            p.weight[0]+= p.lr * p.input[y][0] * error
            p.weight[1]+= p.lr * p.input[y][1] * error

            p.bia += p.lr * error


def calculated(input : list,p : Parameter) -> int:

    result = (input[0] * p.weight[0]) + (input[1] * p.weight[1]) + p.bia

    if result > 0:
        answer = 1
    else:
        answer  = 0

    return answer


if __name__ == "__main__":

    p = prepare()
    train(p, epoch=20)

    for xs in p.input:
        print(xs, "->", calculated(xs, p))