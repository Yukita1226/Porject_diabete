package controller

import (
	"fmt"
	"log"
	"net/http"
	"strings"
	"sync"

	"github.com/gin-gonic/gin"
	ort "github.com/yalue/onnxruntime_go"

	"pk/backend/entity"
)

var ortInitOnce sync.Once
var ortInitErr error

func initOrt(libPath string) error {
	ortInitOnce.Do(func() {
		ort.SetSharedLibraryPath(libPath)
		ortInitErr = ort.InitializeEnvironment()
	})

	if ortInitErr != nil && strings.Contains(strings.ToLower(ortInitErr.Error()), "already") {
		return nil
	}
	return ortInitErr
}

type PerceptronController struct {
	Session *ort.DynamicAdvancedSession
}

func NewPerceptronController(modelPath, libPath string) (*PerceptronController, error) {
	if err := initOrt(libPath); err != nil {
		return nil, fmt.Errorf("ORT init failed (libPath=%s): %w", libPath, err)
	}

	inputInfo, outputInfo, err := ort.GetInputOutputInfo(modelPath)
	if err != nil {
		return nil, fmt.Errorf("failed to get model input/output info: %w", err)
	}
	if len(inputInfo) == 0 || len(outputInfo) == 0 {
		return nil, fmt.Errorf("model structure invalid: no inputs or outputs found")
	}

	inputName := inputInfo[0].Name
	outputName := outputInfo[0].Name
	log.Printf("Model IO: input=%q output=%q", inputName, outputName)

	session, err := ort.NewDynamicAdvancedSession(
		modelPath,
		[]string{inputName},
		[]string{outputName},
		nil,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to load ONNX model: %w", err)
	}

	log.Println("Perceptron model loaded successfully")
	return &PerceptronController{Session: session}, nil
}

func (pc *PerceptronController) Predict(c *gin.Context) {
	var req = entity.Test{}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid JSON"})
		return
	}

	output, err := pc.predict(req.Input1, req.Input2)
	if err != nil {
		log.Println("Inference failed:", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "model not available"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"input1": req.Input1,
		"input2": req.Input2,
		"output": output,
	})
}

func (pc *PerceptronController) predict(x, y float32) (int64, error) {
	// Shape (1, 2): one sample, two features. Float because the ONNX model
	// declared input as TensorProto.FLOAT.
	inputTensor, err := ort.NewTensor(ort.NewShape(1, 2), []float32{x, y})
	if err != nil {
		return 0, fmt.Errorf("create input tensor: %w", err)
	}
	defer inputTensor.Destroy()

	// Shape (1, 1): the ONNX graph ends with Cast(int64) producing one int per sample.
	outputTensor, err := ort.NewEmptyTensor[int64](ort.NewShape(1, 1))
	if err != nil {
		return 0, fmt.Errorf("create output tensor: %w", err)
	}
	defer outputTensor.Destroy()

	if err := pc.Session.Run(
		[]ort.Value{inputTensor},
		[]ort.Value{outputTensor},
	); err != nil {
		return 0, fmt.Errorf("inference: %w", err)
	}

	return outputTensor.GetData()[0], nil
}