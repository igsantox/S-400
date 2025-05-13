def predict_next_candle(sequence):
    """
    Predicts the next 1-minute candle color (GREEN, RED, or Likely Green/Red in uncertain cases)
    based on a 10-color sequence using weighted pattern analysis.
    """
    if len(sequence) != 10 or not set(sequence).issubset({"G", "R", "V"}):
        raise ValueError("Sequence must be 10 characters long, containing only G, R, or V.")

    green_score = red_score = 0

    # Stats
    g_count = sequence.count("G")
    r_count = sequence.count("R")
    last_two = sequence[-2:]
    last_five = sequence[-5:]

    # Scoring logic
    green_score += 2 if last_two == "GG" else 0
    red_score   += 2 if last_two == "RR" else 0

    green_score += 2 if "VG" in sequence else 0
    red_score   += 2 if "VR" in sequence else 0

    red_score   += 2 if "GGG" in sequence else 0
    green_score += 2 if "RRR" in sequence else 0

    red_score   += 1 if all(sequence[i] != sequence[i+1] for i in range(9)) else 0  # Alternating

    green_score += 2 if g_count >= 6 else 0
    red_score   += 2 if r_count >= 6 else 0
    red_score   += 1 if last_five.count("V") >= 2 else 0

    # Decision
    diff = green_score - red_score
    if diff >= 3:
        return "GREEN"
    elif diff <= -3:
        return "RED"
    else:
        # In uncertain range: offer bias
        if diff > 0:
            return "Likely GREEN (~60%)"
        elif diff < 0:
            return "Likely RED (~60%)"
        else:
            return "50/50 - No Clear Edge"

# Example use
sequence = "RGGGGGGRGG"
print("Predicted next candle:", predict_next_candle(sequence))
