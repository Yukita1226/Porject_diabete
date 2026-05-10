import pandas as pd


class Parameter: #
    
    def __init__(self,input = None,output = None,weight = None,lr = None,bia = None):

        self.input = input
        self.output = output
        self.weight = weight
        self.lr = lr     
        self.bia = bia       #learning rate


def prepare(name : str) -> Parameter:

    d = pd.read_csv(name, header=None)
    p  = Parameter()

    p.input = d.iloc[:, :2].values.tolist()
    p.output = d.iloc[:, 2].values.tolist()
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

    p = prepare("data.csv")
    train(p, epoch=20)

    total_true = 0
    total_false = 0

    for i in range(len(p.input)):
        predicted = calculated(p.input[i], p)
        actual = p.output[i]

        if predicted == actual:
            result = True
            total_true += 1
        else:
            result = False
            total_false += 1

        print(p.input[i], "->", predicted, "| expected:", actual, "|", result)

    accuracy = total_true / len(p.input) * 100
    print()
    print("Total true :", total_true)
    print("Total false:", total_false)
    print(f"Accuracy   : {accuracy:.2f}%")