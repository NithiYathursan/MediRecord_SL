import os
import pandas as pd


# Create data folder if it does not exist
os.makedirs("data", exist_ok=True)


# Function 1: Select complaint based on cleaned health text
def choose_complaint(text, index):
    text = str(text).lower()

    if "fever" in text or "dengue" in text:
        return "fever and body pain"

    elif "cough" in text or "respiratory" in text:
        return "cough and breathing difficulty"

    elif "diabetes" in text:
        return "high blood sugar"

    elif "hypertension" in text or "blood pressure" in text:
        return "high blood pressure"

    elif "mental" in text or "stress" in text:
        return "sleep disturbance and stress"

    elif "diarrhea" in text or "vomiting" in text:
        return "vomiting and diarrhea"

    else:
        complaints = [
            "fever and cough",
            "headache",
            "abdominal pain",
            "chest discomfort",
            "knee pain",
            "sore throat",
            "skin rash",
            "dizziness"
        ]

        return complaints[index % len(complaints)]


# Function 2: Create Low, Medium, Good, Excellent notes
def create_note_versions(complaint, index):
    ages = [18, 24, 32, 45, 56, 63, 70]
    genders = ["male", "female"]
    durations = ["1 day", "2 days", "3 days", "5 days", "1 week"]
    temperatures = ["37.8C", "38.2C", "38.5C", "39.0C"]
    bps = ["110/70", "120/80", "130/85", "140/90"]
    pulses = [78, 84, 90, 96, 102]

    medicines = [
        "Paracetamol",
        "ORS",
        "Salbutamol",
        "Antibiotic",
        "Pain relief tablet"
    ]

    age = ages[index % len(ages)]
    gender = genders[index % len(genders)]
    duration = durations[index % len(durations)]
    temperature = temperatures[index % len(temperatures)]
    bp = bps[index % len(bps)]
    pulse = pulses[index % len(pulses)]
    medicine = medicines[index % len(medicines)]

    low_note = (
        f"{age} year old {gender} patient came with {complaint}. "
        f"Medicine given."
    )

    medium_note = (
        f"{age} year old {gender} patient came with {complaint} for {duration}. "
        f"{medicine} given."
    )

    good_note = (
        f"{age} year old {gender} patient came with {complaint} for {duration}. "
        f"Temperature {temperature}. Examination done. "
        f"{medicine} prescribed. Review after 3 days."
    )

    excellent_note = (
        f"{age} year old {gender} patient came with {complaint} for {duration}. "
        f"Temperature {temperature}. BP {bp}. Pulse {pulse}. "
        f"Examination findings recorded. Blood test advised. "
        f"{medicine} prescribed. Review after 3 days."
    )

    records = [
        {
            "medical_note": low_note,
            "quality": "Low",
            "found_details": "Main complaint, Treatment/medicine",
            "missing_details": "Symptom duration, Vital signs, Examination findings, Investigation/test, Follow-up/referral"
        },
        {
            "medical_note": medium_note,
            "quality": "Medium",
            "found_details": "Main complaint, Symptom duration, Treatment/medicine",
            "missing_details": "Vital signs, Examination findings, Investigation/test, Follow-up/referral"
        },
        {
            "medical_note": good_note,
            "quality": "Good",
            "found_details": "Main complaint, Symptom duration, Vital signs, Examination findings, Treatment/medicine, Follow-up/referral",
            "missing_details": "Investigation/test"
        },
        {
            "medical_note": excellent_note,
            "quality": "Excellent",
            "found_details": "Main complaint, Symptom duration, Vital signs, Examination findings, Investigation/test, Treatment/medicine, Follow-up/referral",
            "missing_details": "No major missing details"
        }
    ]

    return records


# Function 3: Create final dataset
def prepare_dataset():
    input_file = "data/clean_srilanka_health_text.csv"
    output_file = "data/medirecord_dataset.csv"

    df = pd.read_csv(input_file)

    print("Cleaned records loaded:", len(df))

    all_rows = []

    for index, row in df.iterrows():
        cleaned_text = row.get("cleaned_text", "")

        complaint = choose_complaint(cleaned_text, index)

        note_versions = create_note_versions(complaint, index)

        for note in note_versions:
            all_rows.append({
                "medical_note": note["medical_note"],
                "quality": note["quality"],
                "found_details": note["found_details"],
                "missing_details": note["missing_details"],
                "source_name": row.get("source_name", ""),
                "source_page": row.get("source_page", ""),
                "pdf_url": row.get("pdf_url", "")
            })

    dataset = pd.DataFrame(all_rows)

    # Remove exact duplicate notes
    dataset.drop_duplicates(subset=["medical_note"], inplace=True)

    # Shuffle dataset
    dataset = dataset.sample(frac=1, random_state=42)

    dataset.to_csv(output_file, index=False, encoding="utf-8")

    print("Dataset created successfully.")
    print("Saved file:", output_file)
    print("Total dataset records:", len(dataset))

    print("\nQuality distribution:")
    print(dataset["quality"].value_counts())

    print("\nSample dataset rows:")
    print(dataset.head())


prepare_dataset()