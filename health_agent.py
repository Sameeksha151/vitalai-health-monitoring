from datetime import datetime
import csv
import os
import requests

LOG_FILE = "health_log.csv"

# Relay alert function
def relay_alert(email, score, summary, recommendations, tips, doctor_advice):

    webhook = "https://hook.relay.app/api/v1/playbook/cmmm1fj9b00jk0qkpgfru2h2z/trigger/PJHZKmn7ls0r5OO9fXP2DQ"

    data = {
    "email": email,
    "score": score,
    "summary": summary,
    "doctor_advice": doctor_advice, 
    "recommendations": "• " + "\n• ".join(recommendations),
    "tips": "• " + "\n• ".join(tips)
}

    requests.post(webhook, json=data)

    try:
        requests.post(webhook, json=data)
    except:
        print("Relay alert failed")

def analyze_health(data: dict, email):

    age = int(data.get("age", 0) or 0)
    sleep_hours = float(data.get("sleep_hours", 0) or 0)
    stress_level = int(data.get("stress_level", 3) or 3)
    mood_level = int(data.get("mood_level", 3) or 3)
    water_liters = float(data.get("water_liters", 0) or 0)
    steps = int(data.get("steps", 0) or 0)
    junk_food = data.get("junk_food", "rare").lower()
    screen_time = float(data.get("screen_time", 0) or 0)
    symptoms = data.get("symptoms", "").strip()

    recommendations = []
    tags = []

    # Sleep analysis
    if sleep_hours < 6:
        recommendations.append(
            "You are sleeping less than 6 hours. Try to aim for 7–8 hours of sleep."
        )
        tags.append("sleep-low")
        sleep_score = 40
    elif 6 <= sleep_hours <= 8:
        recommendations.append(
            "Your sleep duration looks okay."
        )
        sleep_score = 80
    else:
        recommendations.append(
            "You are sleeping more than 8 hours."
        )
        sleep_score = 60

    # Stress analysis
    if stress_level >= 4:
        recommendations.append(
            "Your stress level seems high. Try breathing exercises or short breaks."
        )
        tags.append("stress-high")
        stress_score = 40
    elif stress_level == 3:
        recommendations.append(
            "Stress is moderate."
        )
        stress_score = 65
    else:
        recommendations.append(
            "Great! Your stress level seems low."
        )
        stress_score = 85

    # Mood analysis
    if mood_level <= 2:
        recommendations.append(
            "Your mood seems low. Try doing something you enjoy."
        )
        tags.append("mood-low")
        mood_score = 40
    elif mood_level == 3:
        mood_score = 60
    else:
        mood_score = 85

    # Hydration analysis
    if water_liters < 1.5:
        recommendations.append(
            "You might be drinking less water. Try to drink at least 2 liters."
        )
        tags.append("water-low")
        water_score = 40
    elif 1.5 <= water_liters <= 3:
        water_score = 80
    else:
        water_score = 70

    # Activity analysis
    if steps < 3000:
        recommendations.append(
            "Physical activity seems low. Try walking more."
        )
        tags.append("activity-low")
        activity_score = 40
    elif 3000 <= steps <= 7000:
        activity_score = 70
    else:
        activity_score = 85

    # Food habits
    if junk_food == "often":
        recommendations.append(
            "You are eating junk food often. Try to reduce it."
        )
        tags.append("food-junk")
        food_score = 45
    elif junk_food == "sometimes":
        food_score = 65
    else:
        food_score = 85

    # Screen time
    if screen_time > 6:
        recommendations.append(
            "Screen time is high. Try following the 20-20-20 rule."
        )
        tags.append("screen-high")
        screen_score = 45
    elif 3 <= screen_time <= 6:
        screen_score = 65
    else:
        screen_score = 80

    # Symptoms
    if symptoms:
        recommendations.append(
            f"You mentioned symptoms: '{symptoms}'. If they continue, consult a doctor."
        )
        tags.append("symptoms-present")

    # Health score
    scores = [
        sleep_score,
        stress_score,
        mood_score,
        water_score,
        activity_score,
        food_score,
        screen_score
    ]

    health_score = int(sum(scores) / len(scores))

# -------- HEALTH STATUS + AI TIPS -------- #

    if health_score >= 80:
        status = "Excellent health condition."
        doctor_advice = "🩺 No medical concern detected. Maintain your healthy lifestyle."
        summary = "Overall, your day looks quite healthy."
        tips = [
            "Maintain your current lifestyle habits.",
            "Continue regular exercise and balanced diet.",
            "Stay hydrated and maintain good sleep."
]

    elif health_score >= 60:
        status = "Average health condition."
        doctor_advice = "🩺 Your health is moderate. Improving sleep, hydration, and physical activity is recommended."
        summary = "Your health status is average today."
        tips = [
            "Improve sleep schedule for better recovery.",
            "Increase physical activity or walking.",
            "Reduce screen time before bedtime."
        ]

    else:
        status = "Health risk detected."
        doctor_advice = "🩺 Your health indicators are low. It is recommended to consult a doctor if symptoms persist."
        summary = "Your health indicators are on the lower side today."
        tips = [
            "Increase daily physical activity.",
            "Drink more water and maintain hydration.",
            "Consider consulting a healthcare professional if symptoms continue."
        ]
    # Now relay can use summary

    relay_alert(email, health_score, summary, recommendations, tips, doctor_advice)
    # Log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "age": age,
        "sleep_hours": sleep_hours,
        "stress_level": stress_level,
        "mood_level": mood_level,
        "water_liters": water_liters,
        "steps": steps,
        "junk_food": junk_food,
        "screen_time": screen_time,
        "health_score": health_score,
    }

    log_health(log_entry)

    return {
    "health_score": health_score,
    "summary": summary,
    "status": status,
    "doctor_advice": doctor_advice,
    "recommendations": recommendations,
    "tips": tips,
    "tags": tags,
}



def log_health(entry: dict) -> None:
    file_exists = os.path.isfile(LOG_FILE)

    fieldnames = [
        "timestamp",
        "age",
        "sleep_hours",
        "stress_level",
        "mood_level",
        "water_liters",
        "steps",
        "junk_food",
        "screen_time",
        "health_score"
    ]

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(entry)