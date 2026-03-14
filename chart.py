import matplotlib.pyplot as plt
import sqlite3

def generate_health_chart(user_id):

    conn = sqlite3.connect("vitalai.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT health_score FROM health_logs WHERE user_id=? ORDER BY id",
        (user_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    scores = [r[0] for r in rows]

    if len(scores) == 0:
        scores = [0]

    days = list(range(1, len(scores)+1))

    plt.figure()

    plt.plot(days, scores, marker="o")

    plt.title("Your Health Score Trend")

    plt.xlabel("Entries")

    plt.ylabel("Health Score")

    plt.savefig("static/health_chart.png")

    plt.close()