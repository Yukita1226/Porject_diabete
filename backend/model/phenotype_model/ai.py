import pandas as pd


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
            p.hypertension.append(x)
        else:
            print(f'found hypertrension error at index {l} value : {x}')
            pass
        l+=1
    tem.clear()


    l = 0
    tem  = d.iloc[1:, 3].values.tolist()
    for x in tem:
        if int(x) == 0 or int(x) == 1:
            p.heart_disease.append(x)
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
            p.diabetes.append(x)
        else:
            print(f'found dia error at index {l} value : {x}')
            pass
        l+=1
    tem.clear()


   



    


    p.weight  = [0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01]
    p.lr = 0.001 
    p.bia =0
 
    return p




if __name__ == "__main__":
    print("ok")
    p = prepare("diabetes_prediction_dataset.csv")
    print(p.diabetes)
    print(f'total = {len(p.hypertension)}')
