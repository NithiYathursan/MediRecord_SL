import os
import re
import sqlite3
from datetime import datetime

import joblib
import pandas as pd
import streamlit as st


MODEL_PATH = "models/quality_model.pkl"
DB_NAME = "medirecord_app.db"


# -----------------------------
# Database Functions
# -----------------------------

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS record_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department TEXT,
            medical_note TEXT,
            predicted_quality TEXT,
            confidence REAL,
            completeness_score INTEGER,
            missing_details TEXT,
            suggestion TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_result(department, medical_note, quality, confidence, score, missing_details, suggestion):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO record_analysis (
            department,
            medical_note,
            predicted_quality,
            confidence,
            completeness_score,
            missing_details,
            suggestion,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        department,
        medical_note,
        quality,
        confidence,
        score,
        ", ".join(missing_details),
        suggestion,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_all_records():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM record_analysis ORDER BY id DESC", conn)
    conn.close()
    return df


# -----------------------------
# Text Processing Functions
# -----------------------------

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s./-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def check_record_sections(note):
    text = clean_text(note)

    section_status = {}

    complaint_words = [
        "fever", "cough", "headache", "chest pain", "abdominal pain",
        "vomiting", "diarrhea", "dizziness", "breathing difficulty",
        "rash", "pain", "sore throat", "knee pain"
    ]

    section_status["Main complaint"] = any(word in text for word in complaint_words)

    duration_patterns = [
        r"\bfor\s+\d+\s+(day|days|hour|hours|week|weeks|month|months)",
        r"\bsince\s+(yesterday|morning|evening|last night)",
        r"\d+\s+(day|days|hour|hours|week|weeks|month|months)"
    ]

    section_status["Symptom duration"] = any(
        re.search(pattern, text) for pattern in duration_patterns
    )

    vital_patterns = [
        r"\bbp\s*\d+/\d+",
        r"\bpulse\s*\d+",
        r"\btemperature\s*\d+",
        r"\btemp\s*\d+",
        r"\d+(\.\d+)?\s*c",
        r"\bspo2\s*\d+"
    ]

    section_status["Vital signs"] = any(
        re.search(pattern, text) for pattern in vital_patterns
    )

    examination_words = [
        "examination", "examined", "findings", "abdomen soft",
        "throat redness", "chest clear", "tenderness", "swelling",
        "redness", "lungs clear", "rash present"
    ]

    section_status["Examination findings"] = any(
        word in text for word in examination_words
    )

    investigation_words = [
        "blood test", "urine test", "ecg", "xray", "x-ray",
        "scan", "ct", "mri", "investigation", "test advised"
    ]

    section_status["Investigation / test"] = any(
        word in text for word in investigation_words
    )

    treatment_words = [
        "medicine", "prescribed", "given", "paracetamol",
        "antibiotic", "ors", "tablet", "injection", "treatment",
        "salbutamol"
    ]

    section_status["Treatment / medicine"] = any(
        word in text for word in treatment_words
    )

    followup_words = [
        "review", "follow up", "follow-up", "referred",
        "return if", "clinic", "emergency unit", "after 3 days",
        "after one week"
    ]

    section_status["Follow-up / referral"] = any(
        word in text for word in followup_words
    )

    return section_status


def get_missing_details(section_status):
    missing_details = []

    for section, status in section_status.items():
        if status is False:
            missing_details.append(section)

    return missing_details


def calculate_completeness_score(section_status):
    total_sections = len(section_status)
    completed_sections = 0

    for status in section_status.values():
        if status is True:
            completed_sections = completed_sections + 1

    score = int((completed_sections / total_sections) * 100)
    return score


def generate_suggestion(missing_details):
    if len(missing_details) == 0:
        return "Excellent. The record contains all important medical documentation sections."

    suggestion = "To improve this record, please add: "

    for index, item in enumerate(missing_details):
        if index == len(missing_details) - 1:
            suggestion = suggestion + item
        else:
            suggestion = suggestion + item + ", "

    suggestion = suggestion + "."

    return suggestion


def get_quality_color(quality):
    if quality == "Excellent":
        return "#0f766e"
    elif quality == "Good":
        return "#16a34a"
    elif quality == "Medium":
        return "#d97706"
    else:
        return "#dc2626"


def predict_quality(model, medical_note):
    prediction = model.predict([medical_note])[0]

    confidence = 0

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba([medical_note])[0]
        confidence = round(max(probabilities) * 100, 2)

    return prediction, confidence


# -----------------------------
# Streamlit Page Setup
# -----------------------------

st.set_page_config(
    page_title="MediRecord SL",
    page_icon="🩺",
    layout="wide"
)


# -----------------------------
# Custom CSS
# -----------------------------

st.markdown("""
<style>

.main {
    background-color: #f8fafc;
}

.big-title {
    font-size: 42px;
    font-weight: 800;
    color: #064e3b;
    margin-bottom: 0px;
}

.subtitle {
    font-size: 18px;
    color: #475569;
    margin-top: 0px;
}

.hero-card {
    background: linear-gradient(135deg, #dcfce7, #ecfeff);
    padding: 28px;
    border-radius: 22px;
    border: 1px solid #bbf7d0;
    margin-bottom: 20px;
}

.metric-card {
    background-color: white;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #e2e8f0;
    box-shadow: 0px 4px 18px rgba(15, 23, 42, 0.06);
    text-align: center;
}

.metric-title {
    font-size: 15px;
    color: #64748b;
    font-weight: 600;
}

.metric-value {
    font-size: 30px;
    font-weight: 800;
    color: #064e3b;
}

.section-card-good {
    background-color: #ecfdf5;
    padding: 14px;
    border-radius: 14px;
    border-left: 6px solid #16a34a;
    margin-bottom: 10px;
    color: #065f46;
    font-weight: 600;
}

.section-card-bad {
    background-color: #fef2f2;
    padding: 14px;
    border-radius: 14px;
    border-left: 6px solid #dc2626;
    margin-bottom: 10px;
    color: #991b1b;
    font-weight: 600;
}

.suggestion-card {
    background-color: #eff6ff;
    padding: 18px;
    border-radius: 16px;
    border-left: 6px solid #2563eb;
    color: #1e3a8a;
    font-size: 16px;
}

.warning-card {
    background-color: #fff7ed;
    padding: 16px;
    border-radius: 16px;
    border-left: 6px solid #f97316;
    color: #9a3412;
    font-size: 15px;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------
# Main App
# -----------------------------

create_table()

if not os.path.exists(MODEL_PATH):
    st.error("Model file not found. Please run train_model.py first.")
    st.stop()

model = joblib.load(MODEL_PATH)


if "medical_note" not in st.session_state:
    st.session_state.medical_note = ""


st.markdown("""
<div class="hero-card">
    <div class="big-title">🩺 MediRecord SL</div>
    <div class="subtitle">
        ML-Based Medical Record Quality Checker for Sri Lankan Hospitals
    </div>
    <br>
    <div>
        This system checks whether a medical record is complete, predicts its quality,
        finds missing details, and suggests improvements.
    </div>
</div>
""", unsafe_allow_html=True)


st.markdown("""
<div class="warning-card">
    ⚠️ Educational prototype only. Do not enter real patient name, NIC, phone number, address, or private medical identity details.
</div>
""", unsafe_allow_html=True)


# Sidebar
st.sidebar.title("MediRecord SL")
st.sidebar.write("Navigation")

menu = st.sidebar.radio(
    "Select Page",
    ["Record Analyzer", "Admin Dashboard", "About Project"]
)

st.sidebar.divider()
st.sidebar.subheader("Sample Notes")

sample_low = "Patient came with fever. Medicine given."

sample_medium = (
    "Patient came with cough and breathing difficulty for 2 days. "
    "Salbutamol given."
)

sample_good = (
    "Patient came with fever for 3 days. Temperature 38.5C. "
    "Examination done. Paracetamol prescribed. Review after 3 days."
)

sample_excellent = (
    "Patient came with fever and body pain for 3 days. Temperature 38.5C. "
    "BP 120/80. Pulse 90. Examination findings recorded. Blood test advised. "
    "Paracetamol prescribed. Review after 3 days."
)

if st.sidebar.button("Load Low Quality Sample"):
    st.session_state.medical_note = sample_low

if st.sidebar.button("Load Medium Quality Sample"):
    st.session_state.medical_note = sample_medium

if st.sidebar.button("Load Good Quality Sample"):
    st.session_state.medical_note = sample_good

if st.sidebar.button("Load Excellent Quality Sample"):
    st.session_state.medical_note = sample_excellent


# -----------------------------
# Page 1: Record Analyzer
# -----------------------------

if menu == "Record Analyzer":
    st.header("📋 Medical Record Analyzer")

    left_col, right_col = st.columns([2, 1])

    with left_col:
        department = st.selectbox(
            "Select Hospital Department",
            ["OPD", "Clinic", "Ward", "Emergency Unit", "Other"]
        )

        medical_note = st.text_area(
            "Enter Medical Note",
            height=220,
            key="medical_note",
            placeholder="Enter medical note here..."
        )

        word_count = len(medical_note.split())
        char_count = len(medical_note)

        col_a, col_b = st.columns(2)

        with col_a:
            st.info(f"Word Count: {word_count}")

        with col_b:
            st.info(f"Character Count: {char_count}")

        analyze_button = st.button("🔍 Analyze Record", use_container_width=True)

    with right_col:
        st.subheader("Required Sections")
        st.write("The system checks these 7 sections:")

        required_sections = [
            "Main complaint",
            "Symptom duration",
            "Vital signs",
            "Examination findings",
            "Investigation / test",
            "Treatment / medicine",
            "Follow-up / referral"
        ]

        for section in required_sections:
            st.write("✅", section)

    if analyze_button:
        if medical_note.strip() == "":
            st.error("Please enter a medical note.")
        else:
            quality, confidence = predict_quality(model, medical_note)

            section_status = check_record_sections(medical_note)
            missing_details = get_missing_details(section_status)
            completeness_score = calculate_completeness_score(section_status)
            suggestion = generate_suggestion(missing_details)

            save_result(
                department,
                medical_note,
                quality,
                confidence,
                completeness_score,
                missing_details,
                suggestion
            )

            st.divider()
            st.subheader("📊 Analysis Result")

            quality_color = get_quality_color(quality)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Predicted Quality</div>
                    <div class="metric-value" style="color:{quality_color};">{quality}</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Model Confidence</div>
                    <div class="metric-value">{confidence}%</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Completeness Score</div>
                    <div class="metric-value">{completeness_score}%</div>
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.progress(completeness_score / 100)

            tab1, tab2, tab3 = st.tabs([
                "Section Checklist",
                "Missing Details",
                "Suggestions"
            ])

            with tab1:
                st.subheader("Record Section Checklist")

                for section, status in section_status.items():
                    if status:
                        st.markdown(f"""
                        <div class="section-card-good">
                            ✅ {section} found
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="section-card-bad">
                            ❌ {section} missing
                        </div>
                        """, unsafe_allow_html=True)

            with tab2:
                st.subheader("Missing Details")

                if len(missing_details) == 0:
                    st.success("No major missing details found.")
                else:
                    for item in missing_details:
                        st.error(item)

            with tab3:
                st.subheader("Improvement Suggestion")
                st.markdown(f"""
                <div class="suggestion-card">
                    {suggestion}
                </div>
                """, unsafe_allow_html=True)

            st.success("Record analyzed and saved successfully.")


# -----------------------------
# Page 2: Admin Dashboard
# -----------------------------

elif menu == "Admin Dashboard":
    st.header("📈 Admin Dashboard")

    df = get_all_records()

    if df.empty:
        st.info("No records available yet.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Records", len(df))

        with col2:
            average_score = round(df["completeness_score"].mean(), 2)
            st.metric("Average Completeness", f"{average_score}%")

        with col3:
            latest_quality = df.iloc[0]["predicted_quality"]
            st.metric("Latest Quality", latest_quality)

        st.divider()

        filter_col1, filter_col2 = st.columns(2)

        with filter_col1:
            quality_options = ["All"] + sorted(df["predicted_quality"].dropna().unique().tolist())
            selected_quality = st.selectbox("Filter by Quality", quality_options)

        with filter_col2:
            department_options = ["All"] + sorted(df["department"].dropna().unique().tolist())
            selected_department = st.selectbox("Filter by Department", department_options)

        filtered_df = df.copy()

        if selected_quality != "All":
            filtered_df = filtered_df[filtered_df["predicted_quality"] == selected_quality]

        if selected_department != "All":
            filtered_df = filtered_df[filtered_df["department"] == selected_department]

        st.subheader("Filtered Records")
        st.dataframe(filtered_df, use_container_width=True)

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.subheader("Quality Distribution")
            quality_count = filtered_df["predicted_quality"].value_counts()
            st.bar_chart(quality_count)

        with chart_col2:
            st.subheader("Department Distribution")
            department_count = filtered_df["department"].value_counts()
            st.bar_chart(department_count)

        st.subheader("Common Missing Details")

        missing_items = []

        for item in filtered_df["missing_details"].fillna(""):
            if item.strip() != "":
                parts = item.split(", ")
                missing_items.extend(parts)

        if len(missing_items) > 0:
            missing_df = pd.DataFrame(missing_items, columns=["Missing Detail"])
            missing_count = missing_df["Missing Detail"].value_counts()
            st.bar_chart(missing_count)
        else:
            st.success("No missing details found in selected records.")

        csv_data = filtered_df.to_csv(index=False)

        st.download_button(
            label="Download Filtered Records as CSV",
            data=csv_data,
            file_name="medirecord_filtered_records.csv",
            mime="text/csv",
            use_container_width=True
        )


# -----------------------------
# Page 3: About Project
# -----------------------------

elif menu == "About Project":
    st.header("ℹ️ About MediRecord SL")

    st.markdown("""
    ### Project Title
    **MediRecord SL: ML-Based Medical Record Quality Checker for Sri Lankan Hospitals**

    ### Main Idea
    This project checks the quality of a medical record using Machine Learning and rule-based NLP.

    ### Novelty Features
    - Predicts medical record quality as **Low, Medium, Good, or Excellent**
    - Detects missing documentation sections
    - Gives a completeness score
    - Provides improvement suggestions
    - Stores analyzed records in a local database
    - Provides an admin dashboard with charts and filters

    ### Important Note
    This system does not diagnose diseases.  
    It only checks whether the medical note is properly documented.

    ### Dataset
    Since real hospital records are private, this prototype uses public Sri Lankan health-related documents and artificial OPD-style notes for educational model training.
    """)