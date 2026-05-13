package main

import (
	"log"
	"os"
	"path/filepath"
	"runtime"
	"strings"

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

func serverAddr() string {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	if strings.HasPrefix(port, ":") {
		return port
	}
	return ":" + port
}

func frontendFile(name string) string {
	return filepath.Join("..", "frontend", name)
}

func clinicalDataFile() string {
	return filepath.Join("model", "phenotype_model", "nhanes_diabetes.csv")
}

func genomicDataFile() string {
	return filepath.Join("model", "genetic_model", "synthetic_genomic_unpaired.csv")
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

	r.GET("/", func(c *gin.Context) {
		c.File(frontendFile("index.html"))
	})
	r.GET("/index.html", func(c *gin.Context) {
		c.File(frontendFile("index.html"))
	})
	r.GET("/style.css", func(c *gin.Context) {
		c.File(frontendFile("style.css"))
	})
	r.GET("/script.js", func(c *gin.Context) {
		c.File(frontendFile("script.js"))
	})
	r.GET("/clinical-data.csv", func(c *gin.Context) {
		c.File(clinicalDataFile())
	})
	r.GET("/genomic-data.csv", func(c *gin.Context) {
		c.File(genomicDataFile())
	})
	r.POST("/predict", dc.Predict)
	addr := serverAddr()
	log.Printf("API server listening on http://localhost%s", addr)
	if err := r.Run(addr); err != nil {
		log.Fatal("server failed: ", err)
	}
}
