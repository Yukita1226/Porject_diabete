import pandas as pd
import math
import random


class Parameter:

    def __init__(self):

        self.sex                = []
        self.age                = []
        self.race               = []
        self.bmi                = []
        self.waist_cm           = []
        self.systolic_bp        = []
        self.diastolic_bp       = []
        self.hba1c              = []
        self.total_cholesterol  = []
        self.hdl_cholesterol    = []
        self.diabetes           = []

        self.weight             = []
        self.lr                 = 0.0
        self.bia                = 0.0


def sigmoid(z):

    if z < -500: return 0.0
    if z > 500:  return 1.0
    return 1.0 / (1.0 + math.exp(-z))


def prepare(name: str) -> Parameter:

    d = pd.read_csv(name, header=None)
    p = Parameter()


    # CSV columns: participant_id(0), cycle(1), sex(2), age(3), race(4),
    #              bmi(5), waist_cm(6), systolic_bp(7), diastolic_bp(8),
    #              hba1c(9), total_cholesterol(10), hdl_cholesterol(11), diabetes(12)
    tem = d.iloc[1:, 2].values.tolist();   [p.sex.append(float(x))               for x in tem]; tem.clear()
    tem = d.iloc[1:, 3].values.tolist();   [p.age.append(float(x))               for x in tem]; tem.clear()
    tem = d.iloc[1:, 4].values.tolist();   [p.race.append(float(x))              for x in tem]; tem.clear()
    tem = d.iloc[1:, 5].values.tolist();   [p.bmi.append(float(x))               for x in tem]; tem.clear()
    tem = d.iloc[1:, 6].values.tolist();   [p.waist_cm.append(float(x))          for x in tem]; tem.clear()
    tem = d.iloc[1:, 7].values.tolist();   [p.systolic_bp.append(float(x))       for x in tem]; tem.clear()
    tem = d.iloc[1:, 8].values.tolist();   [p.diastolic_bp.append(float(x))      for x in tem]; tem.clear()
    tem = d.iloc[1:, 9].values.tolist();   [p.hba1c.append(float(x))             for x in tem]; tem.clear()
    tem = d.iloc[1:, 10].values.tolist();  [p.total_cholesterol.append(float(x)) for x in tem]; tem.clear()
    tem = d.iloc[1:, 11].values.tolist();  [p.hdl_cholesterol.append(float(x))   for x in tem]; tem.clear()
    tem = d.iloc[1:, 12].values.tolist();  [p.diabetes.append(int(float(x)))     for x in tem]; tem.clear()

    p.weight = [0.01] * 10
    p.lr     = 0.00001
    p.bia    = 0.0

    return p


def split_data(p: Parameter, test_ratio: float = 0.2):
    n = len(p.diabetes)
    indices = list(range(n))
    random.seed(42)
    random.shuffle(indices)

    test_size = int(n * test_ratio)
    test_idx  = indices[:test_size]
    train_idx = indices[test_size:]

    print(f"Total: {n}  →  Train: {len(train_idx)}  Test: {len(test_idx)}")
    return train_idx, test_idx


def _features(p: Parameter, y: int) -> list:
    return [
        p.sex[y],
        p.age[y],
        p.race[y],
        p.bmi[y],
        p.waist_cm[y],
        p.systolic_bp[y],
        p.diastolic_bp[y],
        p.hba1c[y],
        p.total_cholesterol[y],
        p.hdl_cholesterol[y]
    ]


def train(p: Parameter, epoch: int, train_idx: list) -> None:

    for e in range(epoch):
        total_loss = 0.0

        for y in train_idx:
            x = _features(p, y)

            z = 0
            for i in range(10):
                z += x[i] * p.weight[i]
            z += p.bia
            y_hat = sigmoid(z)

            error = p.diabetes[y] - y_hat
            total_loss += 0.5 * error * error

            for i in range(11):
                p.weight[i] += p.lr * error * x[i]
            p.bia += p.lr * error

        print(f"Epoch {e+1:3d}: loss = {total_loss / len(train_idx):.4f}")


def accuracy(p: Parameter, indices: list, label: str = "") -> None:

    n = len(indices)
    correct = 0
    tp = tn = fp = fn = 0

    ss_res = 0.0
    ss_tot = 0.0
    mean_y = sum(p.diabetes[i] for i in indices) / n

    for y in indices:
        x = _features(p, y)

        z = 0
        for i in range(11):
            z += x[i] * p.weight[i]
        z += p.bia
        y_hat = sigmoid(z)

        pred  = 1 if y_hat >= 0.5 else 0
        truth = p.diabetes[y]

        if pred == truth: correct += 1
        if pred == 1 and truth == 1: tp += 1
        if pred == 0 and truth == 0: tn += 1
        if pred == 1 and truth == 0: fp += 1
        if pred == 0 and truth == 1: fn += 1

        ss_res += (truth - y_hat) ** 2
        ss_tot += (truth - mean_y) ** 2

    acc = correct / n
    r2  = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    print("\n" + "=" * 50)
    print(f"  Accuracy on {label} set")
    print("=" * 50)
    print(f"total samples       : {n}")
    print(f"correct predictions : {correct}")
    print(f"accuracy            : {acc*100:.2f}%")
    print(f"R²                  : {r2:.4f}")
    print("-" * 50)
    print(f"TP: {tp:5d}   FN: {fn:5d}")
    print(f"FP: {fp:5d}   TN: {tn:5d}")
    if (tp + fp) > 0:
        print(f"precision           : {tp/(tp+fp):.4f}")
    if (tp + fn) > 0:
        print(f"recall (sensitivity): {tp/(tp+fn):.4f}")
    print("=" * 50 + "\n")


def calculate(p: Parameter) -> None:

    print("\n" + "=" * 40)
    print("  Diabetes prediction (NHANES)")
    print("=" * 40)

    sex                = float(input("sex (1=male, 2=female) : "))
    age                = float(input("age                    : "))
    race               = float(input("race (1-7)             : "))
    bmi                = float(input("bmi                    : "))
    waist_cm           = float(input("waist_cm               : "))
    systolic_bp        = float(input("systolic_bp            : "))
    diastolic_bp       = float(input("diastolic_bp           : "))
    hba1c              = float(input("hba1c                  : "))
    total_cholesterol  = float(input("total_cholesterol      : "))
    hdl_cholesterol    = float(input("hdl_cholesterol        : "))

    x = [sex, age, race, bmi, waist_cm, systolic_bp, diastolic_bp,
         hba1c, total_cholesterol, hdl_cholesterol]

    z = 0
    for i in range(10):
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

    p = prepare("nhanes_diabetes.csv")

    train_idx, test_idx = split_data(p, test_ratio=0.2)

    train(p, 100, train_idx)

    accuracy(p, train_idx, "TRAIN")
    accuracy(p, test_idx,  "TEST")

    while True:
        calculate(p)
        again = input("test another? (y/n): ").strip().lower()
        if again != "y":
            break