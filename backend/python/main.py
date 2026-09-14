import os
import sys
import json

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

_wire = sys.stdout
sys.stdout = sys.stderr

import numpy as np
import joblib
import keras

MODEL_DIR = "model"

CLINICAL_COLS = ["age", "bmi", "tc", "tg", "hdl", "ldl"]
GENOMIC_COLS  = ["kcnj11", "tcf7l2", "slc30a8", "igf2bp2", "hhex",
                 "cdkn2a", "kcnq1", "cdkal1", "fto"]

sc_clin   = None
sc_meta   = None
mother    = None
clin_full = None
gen_full  = None
clin_embed = None
gen_embed  = None


def loadmodel() -> None:

    global sc_clin, sc_meta, mother, clin_full, gen_full, clin_embed, gen_embed

    sc_clin = joblib.load(f"{MODEL_DIR}/final_mother_clinical_scaler.joblib")
    sc_meta = joblib.load(f"{MODEL_DIR}/final_mother_meta_scaler.joblib")
    mother  = joblib.load(f"{MODEL_DIR}/final_mother_rf.joblib")

    clin_full = keras.models.load_model(f"{MODEL_DIR}/final_mother_clinical_child.keras")
    gen_full  = keras.models.load_model(f"{MODEL_DIR}/final_mother_genomic_child.keras")

    clin_embed = keras.Model(clin_full.input, clin_full.get_layer("clinical_FC").output)
    gen_embed  = keras.Model(gen_full.input,  gen_full.get_layer("genomic_FC").output)


def _vec(payload, cols):

    return np.array([[float(payload[c]) for c in cols]], dtype=np.float32)


def predict_fusion(payload) -> float:

    Xc = _vec(payload["clinical"], CLINICAL_COLS)
    Xg = _vec(payload["genomic"], GENOMIC_COLS)

    Hc = clin_embed.predict(sc_clin.transform(Xc), verbose=0)
    Hg = gen_embed.predict(Xg, verbose=0)

    meta = np.column_stack([Hc, Hg])

    return float(mother.predict_proba(sc_meta.transform(meta))[0, 1])


def predict_clinical(payload) -> float:

    Xc = _vec(payload, CLINICAL_COLS)

    return float(clin_full.predict(sc_clin.transform(Xc), verbose=0)[0, 1])


def predict_genomic(payload) -> float:

    Xg = _vec(payload, GENOMIC_COLS)

    return float(gen_full.predict(Xg, verbose=0)[0, 1])


def serve() -> None:

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        req = json.loads(line)
        cmd = req.get("cmd")
        payload = req.get("payload") or {}

        try:
            if cmd == "predict_fusion":
                data = predict_fusion(payload)
            elif cmd == "predict_clinical":
                data = predict_clinical(payload)
            elif cmd == "predict_genomic":
                data = predict_genomic(payload)
            elif cmd == "ping":
                data = "pong"
            else:
                data = None
        except Exception as e:
            print(repr(e), file=sys.stderr)
            data = None

        _wire.write(json.dumps({"id": req.get("id"), "prob": data}) + "\n")
        _wire.flush()


if __name__ == "__main__":
    loadmodel()
    serve()