import numpy as np
import keras

model = []


def loadmodel() -> list[keras.Model]:

    global model

    model1 = keras.models.load_model(r"model/genomic_mlp_child.keras")
    model2 = keras.models.load_model(r"model/clinical_mlp_child.keras")

    return [model1,model2]

def predict(age = 0,bmi = 0,tc = 0,tg = 0,hdl = 0,ldl = 0)


if __name__ == "__main__" :
    model = loadmodel()
    for  x in model:
        x.summary()

    # x = np.array([[0.5, 1.2, 0.0, 1.0, 0.3, 0.8, 1.0, 0.0, 0.7]], dtype="float32")

    # probs = model.predict(x, verbose=0)

    # print("probabilities:", probs[0])
    # print("predicted class:", int(np.argmax(probs[0])))