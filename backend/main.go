package main

import (
	"log"
	"runtime"

	"github.com/gin-gonic/gin"
	"pk/backend/controller"
)

func libPath() string {
	if runtime.GOOS == "windows" {
		return "lib/onnxruntime.dll"
	}
	return "lib/libonnxruntime.so"
}

func corsMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	}
}

func main() {
	pc, err := controller.NewPerceptronController("model/test(testingonly)/perceptron.onnx", libPath())
	if err != nil {
		log.Fatal(err)
	}

	r := gin.Default()
	r.Use(corsMiddleware())

	r.POST("/predict", pc.Predict)
	r.Run(":8080")
}







input1 = xxx
input xxx
output 1