# MediRecord SL

**MediRecord SL** is an ML-based medical record quality checker designed as an educational prototype for Sri Lankan hospitals. The system checks whether a medical note is complete, predicts the quality of the note, identifies missing documentation sections, and provides improvement suggestions.

This project does **not diagnose diseases**. It only checks the quality and completeness of medical record documentation.

---

## Project Overview

In hospitals, medical records should contain important details such as the main complaint, symptom duration, vital signs, examination findings, investigations, treatment, and follow-up instructions. If these details are missing, the quality of documentation becomes low.

MediRecord SL helps users check the completeness of a medical note using Machine Learning and rule-based NLP techniques.

---

## Main Features

* Predicts medical record quality as:

  * Low
  * Medium
  * Good
  * Excellent
* Detects missing medical record sections
* Calculates completeness score
* Gives improvement suggestions
* Provides an interactive Streamlit interface
* Stores analyzed records using SQLite
* Includes an admin dashboard with charts and filters
* Allows CSV export of analyzed records

---

## Required Medical Record Sections

The system checks whether the following sections are available:

1. Main complaint
2. Symptom duration
3. Vital signs
4. Examination findings
5. Investigation or test
6. Treatment or medicine
7. Follow-up or referral

---

## Technologies Used

* Python
* Streamlit
* SQLite
* Pandas
* Scikit-learn
* TF-IDF Vectorizer
* Logistic Regression
* BeautifulSoup
* Requests
* PyMuPDF
* Joblib

---

## Machine Learning Approach

The model is trained using a text classification approach.

### Input

Medical note text

### Output

Predicted quality label:

* Low
* Medium
* Good
* Excellent

### Model Pipeline

* TF-IDF Vectorizer
* Logistic Regression Classifier

---

## Dataset Information

Real hospital records are private and should not be used without permission. Therefore, this project uses public Sri Lankan health-related documents and artificial OPD-style medical notes for educational model training.

The dataset contains medical notes labelled according to documentation completeness.

### Dataset Labels

* Low: Very few details available
* Medium: Some important details available
* Good: Most details available
* Excellent: All major sections available

---

## Project Structure

```text
MediRecord_SL/
│
├── collect_data.py
├── clean_data.py
├── prepare_dataset.py
├── train_model.py
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   ├── raw_srilanka_health_text.csv
│   ├── clean_srilanka_health_text.csv
│   ├── medirecord_dataset.csv
│   └── skipped_pdfs.csv
│
├── models/
│   ├── quality_model.pkl
│   └── model_report.txt
│
└── screenshots/
    └── interface.png
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/MediRecord_SL.git
```

### 2. Go to the project folder

```bash
cd MediRecord_SL
```

### 3. Install required libraries

```bash
pip install -r requirements.txt
```

---

## How to Run the Project

### Step 1: Collect Data

```bash
python collect_data.py
```

This collects public Sri Lankan health-related PDF text.

### Step 2: Clean Data

```bash
python clean_data.py
```

This cleans and organizes the collected text.

### Step 3: Prepare Dataset

```bash
python prepare_dataset.py
```

This creates labelled medical note data.

### Step 4: Train Model

```bash
python train_model.py
```

This trains the NLP model and saves it in the `models/` folder.

### Step 5: Run Streamlit App

```bash
streamlit run app.py
```

---

## Sample Input

```text
Patient came with fever and body pain for 3 days. Temperature 38.5C. BP 120/80. Pulse 90. Examination findings recorded. Blood test advised. Paracetamol prescribed. Review after 3 days.
```

## Sample Output

```text
Predicted Quality: Excellent
Completeness Score: 100%
Missing Details: No major missing details
Suggestion: The record is complete.
```

---

## Admin Dashboard

The admin dashboard provides:

* Total analyzed records
* Average completeness score
* Quality distribution chart
* Department-wise record count
* Common missing details
* Filtered records table
* CSV download option

---

## Ethical Considerations

This project follows basic privacy and ethical principles:

* No real patient records are used
* No patient names are stored
* No NIC numbers are stored
* No phone numbers or addresses are stored
* The system is only an educational prototype
* The system does not provide medical diagnosis
* The system should not be used in real hospitals without expert validation

---

## Limitations

* The dataset is artificially generated for educational purposes
* The model is not trained on real hospital records
* Prediction accuracy depends on dataset quality
* Rule-based missing detail detection may not understand every writing style
* The system is not a replacement for medical professionals

---

## Future Improvements

* Use anonymized real hospital records with permission
* Improve NLP section detection
* Add user login system
* Add role-based access for doctors and admins
* Add PDF report generation
* Add better model explainability
* Deploy the system online
* Add Sinhala and Tamil language support

---

## Branch Workflow

This project was developed using separate Git branches:

```text
main
data-collection
model-training
streamlit-interface
documentation
```

Each branch was used for a specific development part before merging into `main`.

---

## Project Status

```text
Data Collection       Completed
Data Cleaning         Completed
Dataset Preparation   Completed
Model Training        Completed
Streamlit Interface   Completed
Admin Dashboard       Completed
```

---

## Author

**N. Yathursan**
Department of Data Science
Sabaragamuwa University of Sri Lanka

---

## Disclaimer

MediRecord SL is an academic project. It is not a certified medical system. It should not be used for real clinical decision-making without proper testing, expert review, and approval.
