import pandas as pd
import math
import random


def sigmoid(z: float) -> float:
    if z < -500: return 0.0
    if z > 500:  return 1.0
    return 1.0 / (1.0 + math.exp(-z))


class Parameter:

    def __init__(self):

        self.genotype_SLC30A8   = []
        self.genotype_PAM       = []
        self.genotype_MC4R      = []
        self.genotype_WIPI1     = []
        self.genotype_SOCS2     = []
        self.genotype_HNF1A     = []
        self.genotype_GLP1R     = []
        self.genotype_DYNC2H1   = []
        self.genotype_TM6SF2    = []
        self.genotype_CDKN1B    = []
        self.genotype_JMJD1C    = []
        self.genotype_SSTR5     = []
        self.genotype_ZHX3      = []
        self.genotype_TPCN2     = []
        self.genotype_ASCC2     = []
        self.genotype_PAX4      = []
        self.genotype_PLXND1    = []
        self.genotype_MACF1     = []
        self.genotype_POC5      = []
        self.genotype_PRIM1     = []
        self.genotype_SOS2      = []
        self.genotype_CCDC92    = []
        self.genotype_SETD9     = []
        self.genotype_GCKR      = []
        self.genotype_NYNRIN    = []
        self.genotype_APOE      = []
        self.genotype_ANGPTL4   = []
        self.genotype_KIAA1755  = []
        self.genotype_KCNJ11    = []
        self.genotype_PNPLA3    = []
        self.genotype_SLC16A11  = []
        self.genotype_SPRED2    = []
        self.genotype_BDNF      = []
        self.genotype_CPNE4     = []
        self.genotype_MAFA      = []
        self.genotype_CHRDL1    = []
        self.genotype_TSHZ3     = []


        self.prs_score          = []
        self.prs_normalized     = []
        self.genomic_risk       = []   


        self.weight             = []
        self.lr                 = 0.0
        self.bia                = 0.0


def split_data(p: Parameter, test_ratio: float = 0.2):
    n = len(p.genomic_risk)
    indices = list(range(n))
    random.seed(42)
    random.shuffle(indices)

    test_size = int(n * test_ratio)
    test_idx  = indices[:test_size]
    train_idx = indices[test_size:]

    print(f"Total: {n}  →  Train: {len(train_idx)}  Test: {len(test_idx)}")
    return train_idx, test_idx


def accuracy(p: Parameter, indices: list, label: str = "") -> None:

    n = len(indices)
    correct = 0
    tp = tn = fp = fn = 0

    ss_res = 0.0
    ss_tot = 0.0
    mean_y = sum(p.genomic_risk[i] for i in indices) / n

    for y in indices:
        xs = [
            p.genotype_SLC30A8[y], p.genotype_PAM[y], p.genotype_MC4R[y], p.genotype_WIPI1[y],
            p.genotype_SOCS2[y], p.genotype_HNF1A[y], p.genotype_GLP1R[y], p.genotype_DYNC2H1[y],
            p.genotype_TM6SF2[y], p.genotype_CDKN1B[y], p.genotype_JMJD1C[y], p.genotype_SSTR5[y],
            p.genotype_ZHX3[y], p.genotype_TPCN2[y], p.genotype_ASCC2[y], p.genotype_PAX4[y],
            p.genotype_PLXND1[y], p.genotype_MACF1[y], p.genotype_POC5[y], p.genotype_PRIM1[y],
            p.genotype_SOS2[y], p.genotype_CCDC92[y], p.genotype_SETD9[y], p.genotype_GCKR[y],
            p.genotype_NYNRIN[y], p.genotype_APOE[y], p.genotype_ANGPTL4[y], p.genotype_KIAA1755[y],
            p.genotype_KCNJ11[y], p.genotype_PNPLA3[y], p.genotype_SLC16A11[y], p.genotype_SPRED2[y],
            p.genotype_BDNF[y], p.genotype_CPNE4[y], p.genotype_MAFA[y], p.genotype_CHRDL1[y],
            p.genotype_TSHZ3[y], p.prs_score[y], p.prs_normalized[y]
        ]

        z = 0
        for i in range(39):
            z += xs[i] * p.weight[i]
        z += p.bia
        y_hat = sigmoid(z)

        pred  = 1 if y_hat >= 0.5 else 0
        truth = p.genomic_risk[y]

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
    if (tp + fp) > 0: print(f"precision           : {tp/(tp+fp):.4f}")
    if (tp + fn) > 0: print(f"recall (sensitivity): {tp/(tp+fn):.4f}")
    print("=" * 50 + "\n")

def prepare(name: str) -> Parameter:

    d = pd.read_csv(name, header=None)
    p = Parameter()

    tem = d.iloc[1:, 0].values.tolist();   [p.genotype_SLC30A8.append(int(x))  for x in tem]; tem.clear()
    tem = d.iloc[1:, 1].values.tolist();   [p.genotype_PAM.append(int(x))      for x in tem]; tem.clear()
    tem = d.iloc[1:, 2].values.tolist();   [p.genotype_MC4R.append(int(x))     for x in tem]; tem.clear()
    tem = d.iloc[1:, 3].values.tolist();   [p.genotype_WIPI1.append(int(x))    for x in tem]; tem.clear()
    tem = d.iloc[1:, 4].values.tolist();   [p.genotype_SOCS2.append(int(x))    for x in tem]; tem.clear()
    tem = d.iloc[1:, 5].values.tolist();   [p.genotype_HNF1A.append(int(x))    for x in tem]; tem.clear()
    tem = d.iloc[1:, 6].values.tolist();   [p.genotype_GLP1R.append(int(x))    for x in tem]; tem.clear()
    tem = d.iloc[1:, 7].values.tolist();   [p.genotype_DYNC2H1.append(int(x))  for x in tem]; tem.clear()
    tem = d.iloc[1:, 8].values.tolist();   [p.genotype_TM6SF2.append(int(x))   for x in tem]; tem.clear()
    tem = d.iloc[1:, 9].values.tolist();   [p.genotype_CDKN1B.append(int(x))   for x in tem]; tem.clear()
    tem = d.iloc[1:, 10].values.tolist();  [p.genotype_JMJD1C.append(int(x))   for x in tem]; tem.clear()
    tem = d.iloc[1:, 11].values.tolist();  [p.genotype_SSTR5.append(int(x))    for x in tem]; tem.clear()
    tem = d.iloc[1:, 12].values.tolist();  [p.genotype_ZHX3.append(int(x))     for x in tem]; tem.clear()
    tem = d.iloc[1:, 13].values.tolist();  [p.genotype_TPCN2.append(int(x))    for x in tem]; tem.clear()
    tem = d.iloc[1:, 14].values.tolist();  [p.genotype_ASCC2.append(int(x))    for x in tem]; tem.clear()
    tem = d.iloc[1:, 15].values.tolist();  [p.genotype_PAX4.append(int(x))     for x in tem]; tem.clear()
    tem = d.iloc[1:, 16].values.tolist();  [p.genotype_PLXND1.append(int(x))   for x in tem]; tem.clear()
    tem = d.iloc[1:, 17].values.tolist();  [p.genotype_MACF1.append(int(x))    for x in tem]; tem.clear()
    tem = d.iloc[1:, 18].values.tolist();  [p.genotype_POC5.append(int(x))     for x in tem]; tem.clear()
    tem = d.iloc[1:, 19].values.tolist();  [p.genotype_PRIM1.append(int(x))    for x in tem]; tem.clear()
    tem = d.iloc[1:, 20].values.tolist();  [p.genotype_SOS2.append(int(x))     for x in tem]; tem.clear()
    tem = d.iloc[1:, 21].values.tolist();  [p.genotype_CCDC92.append(int(x))   for x in tem]; tem.clear()
    tem = d.iloc[1:, 22].values.tolist();  [p.genotype_SETD9.append(int(x))    for x in tem]; tem.clear()
    tem = d.iloc[1:, 23].values.tolist();  [p.genotype_GCKR.append(int(x))     for x in tem]; tem.clear()
    tem = d.iloc[1:, 24].values.tolist();  [p.genotype_NYNRIN.append(int(x))   for x in tem]; tem.clear()
    tem = d.iloc[1:, 25].values.tolist();  [p.genotype_APOE.append(int(x))     for x in tem]; tem.clear()
    tem = d.iloc[1:, 26].values.tolist();  [p.genotype_ANGPTL4.append(int(x))  for x in tem]; tem.clear()
    tem = d.iloc[1:, 27].values.tolist();  [p.genotype_KIAA1755.append(int(x)) for x in tem]; tem.clear()
    tem = d.iloc[1:, 28].values.tolist();  [p.genotype_KCNJ11.append(int(x))   for x in tem]; tem.clear()
    tem = d.iloc[1:, 29].values.tolist();  [p.genotype_PNPLA3.append(int(x))   for x in tem]; tem.clear()
    tem = d.iloc[1:, 30].values.tolist();  [p.genotype_SLC16A11.append(int(x)) for x in tem]; tem.clear()
    tem = d.iloc[1:, 31].values.tolist();  [p.genotype_SPRED2.append(int(x))   for x in tem]; tem.clear()
    tem = d.iloc[1:, 32].values.tolist();  [p.genotype_BDNF.append(int(x))     for x in tem]; tem.clear()
    tem = d.iloc[1:, 33].values.tolist();  [p.genotype_CPNE4.append(int(x))    for x in tem]; tem.clear()
    tem = d.iloc[1:, 34].values.tolist();  [p.genotype_MAFA.append(int(x))     for x in tem]; tem.clear()
    tem = d.iloc[1:, 35].values.tolist();  [p.genotype_CHRDL1.append(int(x))   for x in tem]; tem.clear()
    tem = d.iloc[1:, 36].values.tolist();  [p.genotype_TSHZ3.append(int(x))    for x in tem]; tem.clear()

    tem = d.iloc[1:, 37].values.tolist();  [p.prs_score.append(float(x))       for x in tem]; tem.clear()
    tem = d.iloc[1:, 38].values.tolist();  [p.prs_normalized.append(float(x))  for x in tem]; tem.clear()
    tem = d.iloc[1:, 39].values.tolist();  [p.genomic_risk.append(int(x))      for x in tem]; tem.clear()

    p.weight = [0.01] * 39
    p.lr     = 0.001
    p.bia    = 0

    return p


def train(p: Parameter, epoch: int) -> None:

    for e in range(epoch):
        total_loss = 0.0

        for y in range(len(p.genomic_risk)):
            x = [
                p.genotype_SLC30A8[y],
                p.genotype_PAM[y],
                p.genotype_MC4R[y],
                p.genotype_WIPI1[y],
                p.genotype_SOCS2[y],
                p.genotype_HNF1A[y],
                p.genotype_GLP1R[y],
                p.genotype_DYNC2H1[y],
                p.genotype_TM6SF2[y],
                p.genotype_CDKN1B[y],
                p.genotype_JMJD1C[y],
                p.genotype_SSTR5[y],
                p.genotype_ZHX3[y],
                p.genotype_TPCN2[y],
                p.genotype_ASCC2[y],
                p.genotype_PAX4[y],
                p.genotype_PLXND1[y],
                p.genotype_MACF1[y],
                p.genotype_POC5[y],
                p.genotype_PRIM1[y],
                p.genotype_SOS2[y],
                p.genotype_CCDC92[y],
                p.genotype_SETD9[y],
                p.genotype_GCKR[y],
                p.genotype_NYNRIN[y],
                p.genotype_APOE[y],
                p.genotype_ANGPTL4[y],
                p.genotype_KIAA1755[y],
                p.genotype_KCNJ11[y],
                p.genotype_PNPLA3[y],
                p.genotype_SLC16A11[y],
                p.genotype_SPRED2[y],
                p.genotype_BDNF[y],
                p.genotype_CPNE4[y],
                p.genotype_MAFA[y],
                p.genotype_CHRDL1[y],
                p.genotype_TSHZ3[y],
                p.prs_score[y],
                p.prs_normalized[y]
            ]

            z = 0
            for i in range(39):
                z += x[i] * p.weight[i]
            z += p.bia
            y_hat = sigmoid(z)

            error = p.genomic_risk[y] - y_hat
            total_loss += 0.5 * error * error

            for i in range(39):
                p.weight[i] += p.lr * error * x[i]
            p.bia += p.lr * error

        print(f"Epoch {e+1}: loss = {total_loss / len(p.genomic_risk):.4f}")


def calculate(p: Parameter) -> None:

    print("\n" + "=" * 50)
    print("  Genomic risk prediction")
    print("=" * 50)
    print("Enter genotype values (0, 1, or 2 for each gene)")
    print("-" * 50)

    genotype_SLC30A8   = int(input("genotype_SLC30A8   : "))
    genotype_PAM       = int(input("genotype_PAM       : "))
    genotype_MC4R      = int(input("genotype_MC4R      : "))
    genotype_WIPI1     = int(input("genotype_WIPI1     : "))
    genotype_SOCS2     = int(input("genotype_SOCS2     : "))
    genotype_HNF1A     = int(input("genotype_HNF1A     : "))
    genotype_GLP1R     = int(input("genotype_GLP1R     : "))
    genotype_DYNC2H1   = int(input("genotype_DYNC2H1   : "))
    genotype_TM6SF2    = int(input("genotype_TM6SF2    : "))
    genotype_CDKN1B    = int(input("genotype_CDKN1B    : "))
    genotype_JMJD1C    = int(input("genotype_JMJD1C    : "))
    genotype_SSTR5     = int(input("genotype_SSTR5     : "))
    genotype_ZHX3      = int(input("genotype_ZHX3      : "))
    genotype_TPCN2     = int(input("genotype_TPCN2     : "))
    genotype_ASCC2     = int(input("genotype_ASCC2     : "))
    genotype_PAX4      = int(input("genotype_PAX4      : "))
    genotype_PLXND1    = int(input("genotype_PLXND1    : "))
    genotype_MACF1     = int(input("genotype_MACF1     : "))
    genotype_POC5      = int(input("genotype_POC5      : "))
    genotype_PRIM1     = int(input("genotype_PRIM1     : "))
    genotype_SOS2      = int(input("genotype_SOS2      : "))
    genotype_CCDC92    = int(input("genotype_CCDC92    : "))
    genotype_SETD9     = int(input("genotype_SETD9     : "))
    genotype_GCKR      = int(input("genotype_GCKR      : "))
    genotype_NYNRIN    = int(input("genotype_NYNRIN    : "))
    genotype_APOE      = int(input("genotype_APOE      : "))
    genotype_ANGPTL4   = int(input("genotype_ANGPTL4   : "))
    genotype_KIAA1755  = int(input("genotype_KIAA1755  : "))
    genotype_KCNJ11    = int(input("genotype_KCNJ11    : "))
    genotype_PNPLA3    = int(input("genotype_PNPLA3    : "))
    genotype_SLC16A11  = int(input("genotype_SLC16A11  : "))
    genotype_SPRED2    = int(input("genotype_SPRED2    : "))
    genotype_BDNF      = int(input("genotype_BDNF      : "))
    genotype_CPNE4     = int(input("genotype_CPNE4     : "))
    genotype_MAFA      = int(input("genotype_MAFA      : "))
    genotype_CHRDL1    = int(input("genotype_CHRDL1    : "))
    genotype_TSHZ3     = int(input("genotype_TSHZ3     : "))

    prs_score          = float(input("prs_score          : "))
    prs_normalized     = float(input("prs_normalized     : "))

    # pack inputs
    x = [
        genotype_SLC30A8, genotype_PAM, genotype_MC4R, genotype_WIPI1,
        genotype_SOCS2, genotype_HNF1A, genotype_GLP1R, genotype_DYNC2H1,
        genotype_TM6SF2, genotype_CDKN1B, genotype_JMJD1C, genotype_SSTR5,
        genotype_ZHX3, genotype_TPCN2, genotype_ASCC2, genotype_PAX4,
        genotype_PLXND1, genotype_MACF1, genotype_POC5, genotype_PRIM1,
        genotype_SOS2, genotype_CCDC92, genotype_SETD9, genotype_GCKR,
        genotype_NYNRIN, genotype_APOE, genotype_ANGPTL4, genotype_KIAA1755,
        genotype_KCNJ11, genotype_PNPLA3, genotype_SLC16A11, genotype_SPRED2,
        genotype_BDNF, genotype_CPNE4, genotype_MAFA, genotype_CHRDL1,
        genotype_TSHZ3, prs_score, prs_normalized
    ]

    # forward pass
    z = 0
    for i in range(39):
        z += x[i] * p.weight[i]
    z += p.bia
    y_hat = sigmoid(z)

    answer = 1 if y_hat >= 0.5 else 0

    print("-" * 50)
    print(f"raw z       : {z:.4f}")
    print(f"probability : {y_hat:.4f}")
    print(f"prediction  : {answer}  ({'high genomic risk' if answer == 1 else 'low genomic risk'})")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    p = prepare("synthetic_genomic_unpaired.csv")

    train_idx, test_idx = split_data(p, test_ratio=0.2)

    train(p, 100)

    accuracy(p, train_idx, "TRAIN")
    accuracy(p, test_idx,  "TEST")

    while True:
        calculate(p)
        again = input("test another? (y/n): ").strip().lower()
        if again != "y":
            break