import streamlit as st
import pandas as pd
import datetime

def predict_next_candle(sequence):
    if len(sequence) != 10 or not set(sequence).issubset({"G", "R", "V"}):
        return "Invalid input"

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
        return "GREEN"
    elif diff <= -3:
        return "RED"
    else:
        if diff > 0:
            return "Likely GREEN (~60%)"
        elif diff < 0:
            return "Likely RED (~60%)"
        else:
            return "50/50 - No Clear Edge"

def log_prediction(sequence, prediction):
    log_data = pd.DataFrame([{
        "Timestamp": datetime.datetime.now(),
        "Sequence": sequence,
        "Prediction": prediction
    }])
    log_data.to_csv("predictions_log.csv", mode='a', header=False, index=False)

# UI
st.title("🧠 Color Candle Predictor")

sequence = st.text_input("Enter 10-candle sequence (G, R, V):", max_chars=10)

if st.button("Predict"):
    prediction = predict_next_candle(sequence.upper())
    st.success(f"Prediction: **{prediction}**")
    log_prediction(sequence.upper(), prediction)
    st.info("Logged to predictions_log.csv ✅")


# Show recent logs in a table
if st.checkbox("Show Recent Logs"):
    try:
        logs = pd.read_csv("predictions_log.csv", header=None, names=["Timestamp", "Sequence", "Prediction"])
        st.dataframe(logs.tail(10))  # Show last 10 entries
    except FileNotFoundError:
        st.warning("No log file found yet.")
