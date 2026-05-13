import requests
import json

URL = "http://localhost:8080/predict"

# ----------------------------------------------------------------
# TEST 1: Clinical only — low risk (matches Colab Test 1)
# ----------------------------------------------------------------
def test_clinical_low():
    print("\n" + "=" * 60)
    print("TEST 1: Clinical only — low risk")
    print("=" * 60)

    payload = {
        "clinical": {
            "sex": 1, "age": 40, "race": 6,
            "bmi": 29.9, "waist_cm": 102.6,
            "systolic_bp": 152, "diastolic_bp": 84,
            "hba1c": 4.8, "glucose_fasting": 102,
            "total_cholesterol": 223, "hdl_cholesterol": 39
        }
    }
    send(payload, expected_colab_prob=0.030488)


# ----------------------------------------------------------------
# TEST 2: Clinical only — HIGH risk
# ----------------------------------------------------------------
def test_clinical_high():
    print("\n" + "=" * 60)
    print("TEST 2: Clinical only — high risk")
    print("=" * 60)

    payload = {
        "clinical": {
            "sex": 1, "age": 65, "race": 3,
            "bmi": 38.5, "waist_cm": 125.0,
            "systolic_bp": 160, "diastolic_bp": 95,
            "hba1c": 9.2, "glucose_fasting": 210,
            "total_cholesterol": 260, "hdl_cholesterol": 28
        }
    }
    send(payload)


# ----------------------------------------------------------------
# TEST 3: Clinical + Genomic (matches Colab Test 2)
# ----------------------------------------------------------------
def test_full():
    print("\n" + "=" * 60)
    print("TEST 3: Clinical + Genomic")
    print("=" * 60)

    payload = {
        "clinical": {
            "sex": 1, "age": 40, "race": 6,
            "bmi": 29.9, "waist_cm": 102.6,
            "systolic_bp": 152, "diastolic_bp": 84,
            "hba1c": 4.8, "glucose_fasting": 102,
            "total_cholesterol": 223, "hdl_cholesterol": 39
        },
        "genomic": {
            "genotype_SLC30A8":  0, "genotype_PAM":      0,
            "genotype_MC4R":     0, "genotype_WIPI1":    1,
            "genotype_SOCS2":    0, "genotype_HNF1A":    0,
            "genotype_GLP1R":    0, "genotype_DYNC2H1":  2,
            "genotype_TM6SF2":   0, "genotype_CDKN1B":   1,
            "genotype_JMJD1C":   1, "genotype_SSTR5":    0,
            "genotype_ZHX3":     0, "genotype_TPCN2":    1,
            "genotype_ASCC2":    0, "genotype_PAX4":     0,
            "genotype_PLXND1":   0, "genotype_MACF1":    0,
            "genotype_POC5":     0, "genotype_PRIM1":    0,
            "genotype_SOS2":     0, "genotype_CCDC92":   2,
            "genotype_SETD9":    1, "genotype_GCKR":     1,
            "genotype_NYNRIN":   0, "genotype_APOE":     0,
            "genotype_ANGPTL4":  0, "genotype_KIAA1755": 2,
            "genotype_KCNJ11":   1, "genotype_PNPLA3":   2,
            "genotype_SLC16A11": 0, "genotype_SPRED2":   0,
            "genotype_BDNF":     0, "genotype_CPNE4":    0,
            "genotype_MAFA":     0, "genotype_CHRDL1":   1,
            "genotype_TSHZ3":    1
        }
    }
    send(payload, expected_colab_prob=0.030488, expected_genomic_prob=0.000890)


# ----------------------------------------------------------------
# HELPER
# ----------------------------------------------------------------
def send(payload, expected_colab_prob=None, expected_genomic_prob=None):
    try:
        r = requests.post(URL, json=payload, timeout=5)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect — is your Go server running on :8080?")
        return

    if r.status_code != 200:
        print(f"❌ HTTP {r.status_code}")
        print(r.text)
        return

    data = r.json()
    print(json.dumps(data, indent=2))

    if expected_colab_prob is not None:
        diff = abs(data["prob_clinical"] - expected_colab_prob)
        status = "✅" if diff < 0.001 else "❌"
        print(f"{status} clinical prob: got={data['prob_clinical']:.6f}  expected≈{expected_colab_prob}  diff={diff:.6f}")

    if expected_genomic_prob is not None and "prob_genomic" in data:
        diff = abs(data["prob_genomic"] - expected_genomic_prob)
        status = "✅" if diff < 0.001 else "❌"
        print(f"{status} genomic prob:  got={data['prob_genomic']:.6f}  expected≈{expected_genomic_prob}  diff={diff:.6f}")


if __name__ == "__main__":
    test_clinical_low()
    test_clinical_high()
    test_full()