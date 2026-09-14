package main

import (
	"log"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"

	"github.com/gin-gonic/gin"
	"pk/backend/controller"
)

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

func pythonDir() string {
	return filepath.Join("..", "backend/python")
}

func clinicalDataFile() string {
	return filepath.Join("model", "phenotype_model", "nhanes_diabetes.csv")
}

func genomicDataFile() string {
	return filepath.Join("model", "genetic_model", "synthetic_genomic_unpaired.csv")
}

func main() {
	if err := controller.Startbridge(pythonDir(), "main.py"); err != nil {
		log.Fatal(err)
	}
	defer controller.Downbridge()


	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-stop
		controller.Downbridge()
		os.Exit(0)
	}()

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
		c.Header("Cache-Control", "no-store")
		c.File(clinicalDataFile())
	})
	r.GET("/clinical-samples.csv", func(c *gin.Context) {
		c.Header("Cache-Control", "no-store")
		c.File(filepath.Join("model", "test(testingonly)", "clinical_samples.csv"))
	})
	r.GET("/genomic-data.csv", func(c *gin.Context) {
		c.Header("Cache-Control", "no-store")
		c.File(genomicDataFile())
	})

	r.POST("/predict", controller.PredictBoth)
	r.POST("/predict/clinical", controller.PredictClinical)
	r.POST("/predict/genomic", controller.PredictGenomic)
	r.GET("/health", controller.Health)

	addr := serverAddr()
	log.Printf("API server listening on http://localhost%s", addr)
	if err := r.Run(addr); err != nil {
		log.Fatal("server failed: ", err)
	}
}