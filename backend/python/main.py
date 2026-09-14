import os
import sys
import json
import numpy as np
import keras


os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

_wire = sys.stdout
sys.stdout = sys.stderr


model = []


def loadmodel() -> None:

    global model

    model1 = keras.models.load_model(r"model/genomic_mlp_child.keras")
    model2 = keras.models.load_model(r"model/clinical_mlp_child.keras")

    model.append(model1)
    model.append(model2)

def predict_clinical(age:float = 0,bmi:float = 0,tc:float = 0,tg:float = 0,hdl:float = 0,ldl:float = 0) -> float:

    global model

    x   = np.array([[age,bmi,tc,tg,hdl,ldl]], dtype="float32")

    tem = model[1].predict(x, verbose=0)    # [0] is negative and [1] is positive
    tem2 = tem[0].tolist()

    return tem2[1]

def predict_gemome(kcn:float = 0,tcf:float = 0,slc:float = 0,igf:float = 0,hex:float = 0,cdk:float = 0,kcnq:float = 0,cd:float = 0,ft:float = 0) -> float:

    global model

    x   = np.array([[kcn,tcf,slc,igf,hex,cdk,kcnq,cd,ft]], dtype="uint8")

    tem = model[0].predict(x, verbose=0)    # [0] is negative and [1] is positive
    tem2 = tem[0].tolist()

    return tem2[1]


co = ["age", "bmi", "tc", "tg", "hdl", "ldl"]
go  = ["kcnj11", "tcf7l2", "slc30a8", "igf2bp2","hhex", "cdkn2a", "kcnq1", "cdkal1", "fto"]


def serve() -> None:

    for line in sys.stdin:
        line = line.strip()

        if not line:
            continue

        req = json.loads(line)
        cmd = req.get("cmd")
        payload = req.get("payload") or {}

        if cmd == "predict_clinical":
            data = predict_clinical(*[payload[k] for k in co])

        elif cmd == "predict_genomic":
            data = predict_gemome(*[payload[k] for k in go])

        elif cmd == "ping":
            data = "pong"

        else:
            data = None

        _wire.write(json.dumps({"id": req.get("id"), "prob": data}) + "\n")
        _wire.flush()


if __name__ == "__main__" :
    loadmodel()
    predict_clinical()
    serve()