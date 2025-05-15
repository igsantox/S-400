import streamlit as st
import pandas as pd
import datetime
from collections import Counter

# --- Prediction Logic ---
def static_scoring(sequence):
    green_score = red_score = 0

    g_count = sequence.count("G")
    r_count = sequence.count("R")
    last_two = sequence[-2:]
    last_five = sequence[-5:]

    green_score += 2 if last_two == "GG" else 0
    red_score   += 2 if last_two == "RR" else 0
    green_score += 2 if "VG" in sequence else 0
    red_score   += 2 if "VR" in sequence else 0
    red_score   += 2 if "GGG" in sequence else 0
    green_score += 2 if "RRR" in sequence else 0
    red_score   += 1 if all(sequence[i] != sequence[i+1] for i in range(9)) else 0
    green_score += 2 if g_count >= 6 else 0
    red_score   += 2 if r_count >= 6 else 0
    red_score   += 1 if last_five.count("V") >= 2 else 0

    diff = green_score - red_score
    if diff >= 3:
        return "GREEN", 70
    elif diff <= -3:
        return "RED", 70
    elif diff > 0:
        return "Likely GREEN", 60
    elif diff < 0:
        return "Likely RED", 60
    else:
        return "No Clear Edge", 50

def smart_predictor(sequence):
    sequence = sequence.upper()

    if len(sequence) != 10 or not set(sequence).issubset({"G", "R", "V"}):
        return "Invalid Input", 0

    try:
        log_df = pd.read_csv("predictions_log.csv", header=None, names=["Timestamp", "Sequence", "Prediction"])
    except FileNotFoundError:
        return static_scoring(sequence)

    recent_matches = log_df[log_df["Sequence"] == sequence]

    if len(recent_matches) >= 5:
        preds = Counter(recent_matches["Prediction"])
        most_common, count = preds.most_common(1)[0]
        confidence = int((count / len(recent_matches)) * 100)
        return most_common, confidence
    else:
        return static_scoring(sequence)

# --- Logging ---
def log_prediction(sequence, prediction):
    log_data = pd.DataFrame([{
        "Timestamp": datetime.datetime.now(),
        "Sequence": sequence,
        "Prediction": prediction
    }])
    log_data.to_csv("predictions_log.csv", mode='a', header=False, index=False)

def log_actual_outcome(sequence, actual):
    log_data = pd.DataFrame([{
        "Timestamp": datetime.datetime.now(),
        "Sequence": sequence,
        "Actual": actual
    }])
    log_data.to_csv("actual_outcomes.csv", mode='a', header=False, index=False)

# --- Accuracy Tracker ---
def calculate_accuracy():
    try:
        preds = pd.read_csv("predictions_log.csv", header=None, names=["Timestamp", "Sequence", "Prediction"])
        actuals = pd.read_csv("actual_outcomes.csv", header=None, names=["Timestamp", "Sequence", "Actual"])
        merged = pd.merge(preds, actuals, on="Sequence", suffixes=("_pred", "_actual"))
        correct = sum(
            merged["Prediction"].str.contains("GREEN") & (merged["Actual"] == "G") |
            merged["Prediction"].str.contains("RED") & (merged["Actual"] == "R")
        )
        total = len(merged)
        accuracy = (correct / total) * 100 if total > 0 else 0
        return accuracy, total
    except Exception:
        return 0, 0

# --- Streamlit UI ---
st.title("🎯 Smart Color Candle Predictor")

sequence = st.text_input("Enter 10-candle sequence (G, R, V):", max_chars=10)

if st.button("Predict"):
    prediction, confidence = smart_predictor(sequence.upper())
    if prediction == "Invalid Input":
        st.error("Please enter a valid 10-letter sequence using only G, R, V.")
    else:
        st.success(f"Prediction: **{prediction}** ({confidence}% confidence)")
        log_prediction(sequence.upper(), prediction)
        st.info("Logged to predictions_log.csv ✅")

if st.checkbox("Show Recent Predictions"):
    try:
        logs = pd.read_csv("predictions_log.csv", header=None, names=["Timestamp", "Sequence", "Prediction"])
        st.dataframe(logs.tail(10))
    except FileNotFoundError:
        st.warning("No prediction logs yet.")

if st.checkbox("Submit Actual Outcome"):
    actual = st.radio("Select actual color:", ["G", "R", "V"])
    if st.button("Submit Actual"):
        log_actual_outcome(sequence.upper(), actual)
        st.success("Actual outcome logged to actual_outcomes.csv ✅")

if st.checkbox("Show Prediction Accuracy"):
    accuracy, total = calculate_accuracy()
    st.metric(label="Prediction Accuracy", value=f"{accuracy:.2f}%")
    st.caption(f"Based on {total} matched predictions.")
