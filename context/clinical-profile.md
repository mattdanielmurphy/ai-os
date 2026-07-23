# Clinical Profile & Research Baseline

This context file defines the baseline demographics, physiological metrics, active medications, lifestyle parameters, and location bounds used by the Clinical Trial Scraper & AI Evaluator (Jules).

---

## 👤 Demographics & Physical Metrics
- **Age:** 28 years old
- **Sex / Gender:** Male
- **Height:** 6'1" – 6'2" (185–188 cm)
- **Weight:** ~265 lbs (~120 kg)
- **BMI:** ~34.5 kg/m² (Class I Obesity)
- **Smoking Status:** Non-nicotine smoker

## 🏋️ Lifestyle & Baseline Activity
- **Substance Use:** Daily cannabis user
- **Physical Activity:** Low / sedentary baseline activity level
- **Resistance Training:** No recent heavy resistance training history (past 3 months)

## 💊 Active Medications & Supplements
- **Mounjaro (tirzepatide):** 7.5 mg/week (GLP-1/GIP dual agonist)
- **Fluoxetine (Prozac):** 20 mg/day (SSRI)
- **Vitamin D:** 1,500 IU/day

## 📍 Geographic Location & Radius
- **Primary Location:** Fort Saskatchewan / Edmonton Metropolitan Area, Alberta, Canada
- **Target Radius:** Within 50 miles (~80 km) of Edmonton (includes University of Alberta North Campus / Health Sciences facilities)

## 🎯 Trial Evaluation & Exclusion Criteria Rules
- **High Sensitivity Criteria to Evaluate:**
  1. **BMI / Weight Limits:** Verify if study requires specific BMI window or excludes BMI > 30 / > 35.
  2. **GLP-1 / Weight Loss Medication Exclusions:** Check if Mounjaro (tirzepatide) or concurrent weight loss treatments are disallowed.
  3. **Cannabis Restrictions:** Check for drug screen exclusions or active cannabinoid restrictions.
  4. **SSRI / Psychiatric Medication Exclusions:** Check for psychotropic/SSRI washouts or exclusions (Fluoxetine).
  5. **Exercise & Physical Requirements:** Check if study requires prior resistance training baseline or specific fitness levels.
  6. **Healthy Volunteer Status:** Include healthy volunteer trials as well as trials evaluating targeted metabolic/lifestyle conditions.
- **Evaluation Outcomes:**
  - `MATCH`: Fits profile criteria with no hard disqualifiers.
  - `UNCERTAIN`: Potential match with minor ambiguity requiring manual review.
  - `INELIGIBLE`: Hard disqualifiers present (e.g. strict medication exclusion, age out of bounds). *Note: Ineligible trials are ignored.*
