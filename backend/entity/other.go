package entity

type Prediction_response struct {
	Prob_clinical       float32 `json:"prob_clinical"`
	Prob_genomic        float32 `json:"prob_genomic,omitempty"`
	Prob_mother         float32 `json:"prob_mother,omitempty"`
	Prediction_clinical string  `json:"prediction_clinical"`
	Prediction_final    string  `json:"prediction_final"`
	Mode                string  `json:"mode"`
}

func (g *Genomic_data) ToRawSlice() []float32 {
	return []float32{
		float32(g.Genotype_SLC30A8),
		float32(g.Genotype_PAM),
		float32(g.Genotype_MC4R),
		float32(g.Genotype_WIPI1),
		float32(g.Genotype_SOCS2),
		float32(g.Genotype_HNF1A),
		float32(g.Genotype_GLP1R),
		float32(g.Genotype_DYNC2H1),
		float32(g.Genotype_TM6SF2),
		float32(g.Genotype_CDKN1B),
		float32(g.Genotype_JMJD1C),
		float32(g.Genotype_SSTR5),
		float32(g.Genotype_ZHX3),
		float32(g.Genotype_TPCN2),
		float32(g.Genotype_ASCC2),
		float32(g.Genotype_PAX4),
		float32(g.Genotype_PLXND1),
		float32(g.Genotype_MACF1),
		float32(g.Genotype_POC5),
		float32(g.Genotype_PRIM1),
		float32(g.Genotype_SOS2),
		float32(g.Genotype_CCDC92),
		float32(g.Genotype_SETD9),
		float32(g.Genotype_GCKR),
		float32(g.Genotype_NYNRIN),
		float32(g.Genotype_APOE),
		float32(g.Genotype_ANGPTL4),
		float32(g.Genotype_KIAA1755),
		float32(g.Genotype_KCNJ11),
		float32(g.Genotype_PNPLA3),
		float32(g.Genotype_SLC16A11),
		float32(g.Genotype_SPRED2),
		float32(g.Genotype_BDNF),
		float32(g.Genotype_CPNE4),
		float32(g.Genotype_MAFA),
		float32(g.Genotype_CHRDL1),
		float32(g.Genotype_TSHZ3),
	}
}
type Prediction_request struct {
    Clinical Phenotype_data `json:"clinical"`
    Genomic  *Genomic_data  `json:"genomic,omitempty"`
}

type Preprocessing_config struct {
    Clinical Scaler_config `json:"clinical"`
    Genomic  Scaler_config `json:"genomic"`
}

type Scaler_config struct {
    Scaler_mean      []float32 `json:"scaler_mean"`
    Scaler_std       []float32 `json:"scaler_std"`
    Selected_indices []int     `json:"selected_indices,omitempty"`
}

func (c *Phenotype_data) ToRawSlice() []float32 {
	return []float32{
		float32(c.Sex),
		c.Age,
		float32(c.Race),
		c.Bmi,
		c.Waist_cm,
		c.Systolic_bp,
		c.Diastolic_bp,
		c.Hba1c,
		c.Glucose_fasting,
		c.Total_cholesterol,
		c.Hdl_cholesterol,
	}
}