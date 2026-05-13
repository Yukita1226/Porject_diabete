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
	dc, err := controller.NewDiabetesController(
		"model/onnx/clinical_model.onnx",
		"model/onnx/genomic_model.onnx",
		"model/onnx/preprocessing_config.json",
		libPath(),
	)
	if err != nil {
		log.Fatal(err)
	}

	r := gin.Default()
	r.Use(corsMiddleware())

	r.POST("/predict", dc.Predict)
	r.Run(":8080")
}