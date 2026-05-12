import os
import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper
 
from test import Parameter, prepare, train
 
 
def build_onnx(weight: list, bia: float, out_path: str) -> None:
    """Bake trained weight + bias into an ONNX graph and save it."""
    W = np.array([[weight[0]], [weight[1]]], dtype=np.float32)
    b = np.array([bia], dtype=np.float32)
 
    W_init = numpy_helper.from_array(W, name="W")
    b_init = numpy_helper.from_array(b, name="b")
    zero   = numpy_helper.from_array(np.array([0.0], dtype=np.float32), name="zero")
 
    input_tensor  = helper.make_tensor_value_info("input",  TensorProto.FLOAT, ["N", 2])
    output_tensor = helper.make_tensor_value_info("output", TensorProto.INT64, ["N", 1])
 
    nodes = [
        helper.make_node("MatMul",  ["input", "W"],     ["xw"],     name="matmul"),
        helper.make_node("Add",     ["xw", "b"],        ["xw_b"],   name="add_bias"),
        helper.make_node("Greater", ["xw_b", "zero"],   ["is_pos"], name="step"),
        helper.make_node("Cast",    ["is_pos"],         ["output"], name="to_int",
                         to=TensorProto.INT64),
    ]
 
    graph = helper.make_graph(
        nodes=nodes,
        name="dumb_perceptron",
        inputs=[input_tensor],
        outputs=[output_tensor],
        initializer=[W_init, b_init, zero],
    )
 
    model = helper.make_model(
        graph,
        producer_name="perceptron-export",
        opset_imports=[helper.make_opsetid("", 13)],
    )
    model.ir_version = 8
    onnx.checker.check_model(model)
    onnx.save(model, out_path)
 
 
if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    csv_path  = os.path.join(here, "data.csv")
    onnx_path = os.path.join(here, "perceptron.onnx")
 
    p = prepare(csv_path)
    train(p, epoch=100)
 
    print(f"Trained weights: {p.weight}")
    print(f"Trained bias:    {p.bia}")
 
    build_onnx(p.weight, p.bia, onnx_path)
    print(f"Wrote {onnx_path}")