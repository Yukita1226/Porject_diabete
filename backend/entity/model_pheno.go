package entity

type Phenotype_data struct {

	Gender	  				string		`json:"gender"`
	Age	      				int64		`json:"age"`
	Hypertension    		bool		`json:"hypertension"`
	Heart_disease    		bool		`json:"heart_disease"`
	Smoking_history    		string		`json:"is_smokeing"`
	Bmi			    		float32		`json:"bmi"`
	HbA1c_level    			float32		`json:"hba1c"`
	Blood_glucose_level    	int			`json:"blood_g_lv"`
	Diabetes	   			bool		`json:"dia"`

}