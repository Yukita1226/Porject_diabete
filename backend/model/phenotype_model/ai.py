import pandas as pd
import math

class Parameter: #
    
    def __init__(self,gender = [],age = [], hypertension = [],heart_disease = [],smoking_history = [],bmi = [],hbA1c_level = [],blood_glucose_level = [],diabetes = [],weight = [],lr = [],bia  = []):

        self.gender             = gender
        self.age                = age
        self.hypertension       = hypertension
        self.heart_disease      = heart_disease
        self.smoking_history    = smoking_history
        self.bmi                = bmi
        self.hbA1c_level        = hbA1c_level
        self.blood_glucose_level= blood_glucose_level
        self.diabetes           = diabetes

        self.weight             = weight
        self.lr                 = lr
        self.bia                = bia

def sigmoid(z):
    if z < -500: return 0.0
    if z > 500:  return 1.0
    return 1.0 / (1.0 + math.exp(-z))

def prepare(name : str) -> Parameter:

    d = pd.read_csv(name, header=None)
    p  = Parameter()


    l = 0
    tem = d.iloc[1:, 0].values.tolist() #2 for male 1 for other and 0 for female
    for x in tem:
        if (x == "Male"):
            p.gender.append(2)
        elif(x == "Other"):
            p.gender.append(1)
        elif(x == "Female"):
            p.gender.append(0)
        else:
            print(f'found gender error at index {l} value : {x}')
            pass
        l+=1
    tem.clear()


    l = 0
    tem = d.iloc[1:, 1].values.tolist()
    for x in tem:
        try:
            p.age.append(float(x))  

        except (ValueError, TypeError):
            print(f'found age error at index {l} value : {x}')

        finally:
            l+=1

    tem.clear()


    l = 0
    tem  = d.iloc[1:, 2].values.tolist()
    for x in tem:
        if int(x) == 0 or int(x) == 1:
            p.hypertension.append(int(x))
        else:
            print(f'found hypertrension error at index {l} value : {x}')
            pass
        l+=1
    tem.clear()


    l = 0
    tem  = d.iloc[1:, 3].values.tolist()
    for x in tem:
        if int(x) == 0 or int(x) == 1:
            p.heart_disease.append(int(x))
        else:
            print(f'found heart_disease error at index {l} value : {x}')
            pass
        l+=1
    tem.clear()


    l = 0
    tem = d.iloc[1:, 4].values.tolist()  #never = 1 , noinfo = -1 former = 2 ,notcurrent = 3,current = 4,ever = 5
    for x in tem:

        if(x == "No Info"):
            p.smoking_history.append(-1)
        elif(x == "never"):
            p.smoking_history.append(1)
        elif(x == "former"):
            p.smoking_history.append(2)
        elif(x == "not current"):
            p.smoking_history.append(4)
        elif(x == "current"):
            p.smoking_history.append(4)
        elif(x == "ever"):
            p.smoking_history.append(5)
        else:
            print(f'found smoking error at index {l} value : {x}')
            pass
        l+=1
    tem.clear()

    l = 0
    tem = d.iloc[1:, 5].values.tolist()
    for x in tem:
        try:
            p.bmi.append(float(x))  
        except (ValueError, TypeError):
            print(f'found bmi error at index {l} value : {x}')

        finally:
            l+=1
    tem.clear()


    l = 0
    tem = d.iloc[1:, 6].values.tolist()
    for x in tem:
        try:
            p.hbA1c_level.append(float(x))  
        except (ValueError, TypeError):
            print(f'found hb1ac error at index {l} value : {x}')

        finally:
            l+=1
    tem.clear()


    l = 0
    tem = d.iloc[1:, 7].values.tolist()
    for x in tem:
        try:
            p.blood_glucose_level.append(int(x))  
        except (ValueError, TypeError):
            print(f'found blood_glucose error at index {l} value : {x}')

        finally:
            l+=1
    tem.clear()

    l = 0
    tem  = d.iloc[1:, 8].values.tolist()
    for x in tem:
        if int(x) == 0 or int(x) == 1:
            p.diabetes.append(int(x))
        else:
            print(f'found dia error at index {l} value : {x}')
            pass
        l+=1
    tem.clear()


   



    


    p.weight  = [0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01]
    p.lr = 0.001 
    p.bia =0
 
    return p

def train(p: Parameter, epoch: int) -> None:

    for e in range(epoch):
        total_loss = 0.0

        for y in range(len(p.diabetes)):
            x = [
                p.gender[y],
                p.age[y],
                p.hypertension[y],
                p.heart_disease[y],
                p.smoking_history[y],
                p.bmi[y],
                p.hbA1c_level[y],
                p.blood_glucose_level[y]
            ]

            z = 0
            for i in range(8):
                z += x[i] * p.weight[i]
            z += p.bia
            y_hat = sigmoid(z)

            error = p.diabetes[y] - y_hat
            total_loss += 0.5 * error * error


            for i in range(8):
                p.weight[i] += p.lr * error * x[i]
            p.bia += p.lr * error

        print(f"Epoch {e+1}: loss = {total_loss / len(p.diabetes):.4f}")

def calculate(p: Parameter) -> None:

    print("\n" + "=" * 40)
    print("  Diabetes prediction")
    print("=" * 40)

    gender_str = input("gender (Male / Female / Other): ").strip()
    if gender_str == "Male":
        gender = 2
    elif gender_str == "Other":
        gender = 1
    elif gender_str == "Female":
        gender = 0
    else:
        print("invalid gender, defaulting to Female (0)")
        gender = 0

    age                 = float(input("age                 : "))
    hypertension        = int(input("hypertension (0/1)  : "))
    heart_disease       = int(input("heart_disease (0/1) : "))

    smoke_str = input("smoking (No Info/never/former/not current/current/ever): ").strip()
    smoke_map = {"No Info": -1, "never": 1, "former": 2,
                 "not current": 4, "current": 4, "ever": 5}
    smoking_history = smoke_map.get(smoke_str, -1)
    if smoke_str not in smoke_map:
        print("invalid smoking, defaulting to No Info (-1)")

    bmi                 = float(input("bmi                 : "))
    hbA1c_level         = float(input("hbA1c_level         : "))
    blood_glucose_level = int(input("blood_glucose_level : "))

    # pack inputs
    x = [gender, age, hypertension, heart_disease,
         smoking_history, bmi, hbA1c_level, blood_glucose_level]

    # forward pass
    z = 0
    for i in range(8):
        z += x[i] * p.weight[i]
    z += p.bia
    y_hat = sigmoid(z)

    answer = 1 if y_hat >= 0.5 else 0

    print("-" * 40)
    print(f"raw z       : {z:.4f}")
    print(f"probability : {y_hat:.4f}")
    print(f"prediction  : {answer}  ({'diabetes' if answer == 1 else 'no diabetes'})")
    print("=" * 40 + "\n")

if __name__ == "__main__":
    print("ok")

    p = prepare("diabetes_prediction_dataset.csv")
    train(p,100)

    while True:
        calculate(p)
        again = input("test another? (y/n): ").strip().lower()
        if again != "y":
            break




