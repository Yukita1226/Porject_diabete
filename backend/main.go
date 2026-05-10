package main

import (
    "log"
    "runtime"

    "github.com/gin-gonic/gin"
    "pk/backend/controller"   // or whatever your folder is named
)

func libPath() string {
    if runtime.GOOS == "windows" {
        return "lib/onnxruntime.dll"
    }
    return "lib/libonnxruntime.so"
}

func main() {
    // 1. Create controller (this loads the ONNX model into memory ONCE)
    pc, err := controller.NewPerceptronController("model/perceptron.onnx", libPath())
    if err != nil {
        log.Fatal(err)
    }

    r := gin.Default()
    r.POST("/predict",pc.Predict) 
    r.Run(":8080")
}