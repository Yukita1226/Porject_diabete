package controller

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
	"net/http"
	"os"
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

const (
	motherW1 = float32(4.213) 
	motherW2 = float32(3.876) 
	motherB  = float32(-3.521) 
)

type DiabetesController struct {
	ClinicalSess *ort.DynamicAdvancedSession
	GenomicSess  *ort.DynamicAdvancedSession

	ClinicalInputName string
	ClinicalOutName   string
	GenomicInputName  string
	GenomicOutName    string

	Config entity.Preprocessing_config
}


func NewDiabetesController(
	clinicalPath, genomicPath, configPath, libPath string,
) (*DiabetesController, error) {

	if err := initOrt(libPath); err != nil {
		return nil, fmt.Errorf("ORT init failed: %w", err)
	}

	// Load preprocessing config
	cfgBytes, err := os.ReadFile(configPath)
	if err != nil {
		return nil, fmt.Errorf("read config: %w", err)
	}
	var cfg entity.Preprocessing_config
	if err := json.Unmarshal(cfgBytes, &cfg); err != nil {
		return nil, fmt.Errorf("parse config: %w", err)
	}

	// Load clinical model
	clinSess, clinInName, clinOutName, err := loadSingleOutputModel(clinicalPath)
	if err != nil {
		return nil, fmt.Errorf("load clinical: %w", err)
	}
	log.Printf("Clinical model: in=%q out=%q", clinInName, clinOutName)

	// Load genomic model
	genSess, genInName, genOutName, err := loadSingleOutputModel(genomicPath)
	if err != nil {
		return nil, fmt.Errorf("load genomic: %w", err)
	}
	log.Printf("Genomic model: in=%q out=%q", genInName, genOutName)

	log.Println("All models loaded successfully")
	return &DiabetesController{
		ClinicalSess:      clinSess,
		GenomicSess:       genSess,
		ClinicalInputName: clinInName,
		ClinicalOutName:   clinOutName,
		GenomicInputName:  genInName,
		GenomicOutName:    genOutName,
		Config:            cfg,
	}, nil
}

func loadSingleOutputModel(path string) (*ort.DynamicAdvancedSession, string, string, error) {
	inputInfo, outputInfo, err := ort.GetInputOutputInfo(path)
	if err != nil {
		return nil, "", "", err
	}
	if len(inputInfo) == 0 || len(outputInfo) == 0 {
		return nil, "", "", fmt.Errorf("no inputs/outputs in %s", path)
	}
	inName := inputInfo[0].Name
	outName := outputInfo[0].Name
	sess, err := ort.NewDynamicAdvancedSession(path, []string{inName}, []string{outName}, nil)
	return sess, inName, outName, err
}


func (dc *DiabetesController) Predict(c *gin.Context) {
	var req entity.Prediction_request
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid JSON: " + err.Error()})
		return
	}

	resp, err := dc.runPipeline(&req)
	if err != nil {
		log.Println("Inference failed:", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "model failure: " + err.Error()})
		return
	}
	c.JSON(http.StatusOK, resp)
}


func (dc *DiabetesController) runPipeline(req *entity.Prediction_request) (*entity.Prediction_response, error) {


	clinicalRaw := req.Clinical.ToRawSlice()
	clinicalScaled, err := zScore(clinicalRaw, dc.Config.Clinical.Scaler_mean, dc.Config.Clinical.Scaler_std)
	if err != nil {
		return nil, fmt.Errorf("clinical scaling: %w", err)
	}

	probClinical, err := dc.runClinical(clinicalScaled)
	if err != nil {
		return nil, fmt.Errorf("clinical inference: %w", err)
	}

	resp := &entity.Prediction_response{
		Prob_clinical:       probClinical,
		Prediction_clinical: labelFromProb(probClinical),
	}

	if req.Genomic == nil {
		resp.Prediction_final = resp.Prediction_clinical
		resp.Mode = "clinical only"
		return resp, nil
	}

	genomicRaw := req.Genomic.ToRawSlice()
	genomicScaledAll, err := zScore(genomicRaw, dc.Config.Genomic.Scaler_mean, dc.Config.Genomic.Scaler_std)
	if err != nil {
		return nil, fmt.Errorf("genomic scaling: %w", err)
	}

	genomicSelected, err := selectFeatures(genomicScaledAll, dc.Config.Genomic.Selected_indices)
	if err != nil {
		return nil, fmt.Errorf("genomic feature selection: %w", err)
	}

	probGenomic, err := dc.runGenomic(genomicSelected)
	if err != nil {
		return nil, fmt.Errorf("genomic inference: %w", err)
	}

	probMother := runMother(probClinical, probGenomic)

	resp.Prob_genomic = probGenomic
	resp.Prob_mother = probMother
	resp.Prediction_final = labelFromProb(probMother)
	resp.Mode = "clinical + genomic (Mother Model)"
	return resp, nil
}

func (dc *DiabetesController) runClinical(scaled []float32) (float32, error) {
	inTensor, err := ort.NewTensor(ort.NewShape(1, int64(len(scaled))), scaled)
	if err != nil {
		return 0, err
	}
	defer inTensor.Destroy()

	outTensor, err := ort.NewEmptyTensor[float32](ort.NewShape(1, 1))
	if err != nil {
		return 0, err
	}
	defer outTensor.Destroy()

	if err := dc.ClinicalSess.Run([]ort.Value{inTensor}, []ort.Value{outTensor}); err != nil {
		return 0, err
	}
	return outTensor.GetData()[0], nil
}

func (dc *DiabetesController) runGenomic(scaled []float32) (float32, error) {
	inTensor, err := ort.NewTensor(ort.NewShape(1, int64(len(scaled))), scaled)
	if err != nil {
		return 0, err
	}
	defer inTensor.Destroy()

	outTensor, err := ort.NewEmptyTensor[float32](ort.NewShape(1, 1))
	if err != nil {
		return 0, err
	}
	defer outTensor.Destroy()

	if err := dc.GenomicSess.Run([]ort.Value{inTensor}, []ort.Value{outTensor}); err != nil {
		return 0, err
	}
	return outTensor.GetData()[0], nil
}

func runMother(probClinical, probGenomic float32) float32 {
	z := motherW1*probClinical + motherW2*probGenomic + motherB
	return float32(1.0 / (1.0 + math.Exp(-float64(z))))
}

func zScore(raw, mean, std []float32) ([]float32, error) {
	if len(raw) != len(mean) || len(raw) != len(std) {
		return nil, fmt.Errorf("length mismatch: raw=%d mean=%d std=%d", len(raw), len(mean), len(std))
	}
	out := make([]float32, len(raw))
	for i := range raw {
		if std[i] == 0 {
			out[i] = 0
		} else {
			out[i] = (raw[i] - mean[i]) / std[i]
		}
	}
	return out, nil
}

func selectFeatures(all []float32, idx []int) ([]float32, error) {
	out := make([]float32, len(idx))
	for i, j := range idx {
		if j < 0 || j >= len(all) {
			return nil, fmt.Errorf("selected index %d out of range [0,%d)", j, len(all))
		}
		out[i] = all[j]
	}
	return out, nil
}

func labelFromProb(p float32) string {
	if p >= 0.5 {
		return "diabetes"
	}
	return "no diabetes"
}