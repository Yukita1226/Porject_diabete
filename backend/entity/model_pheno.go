package entity

type Phenotype_data struct {
	Sex               int8    `json:"sex"`              
	Age               float32 `json:"age"`
	Race              int8    `json:"race"`           
	Bmi               float32 `json:"bmi"`
	Waist_cm          float32 `json:"waist_cm"`
	Systolic_bp       float32 `json:"systolic_bp"`
	Diastolic_bp      float32 `json:"diastolic_bp"`
	Hba1c             float32 `json:"hba1c"`
	Glucose_fasting   float32 `json:"glucose_fasting"`
	Total_cholesterol float32 `json:"total_cholesterol"`
	Hdl_cholesterol   float32 `json:"hdl_cholesterol"`
}