from flask import Flask, render_template, request, jsonify, session
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey123"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

subjects = {
    "toan": "Toán",
    "van": "Ngữ văn",
    "anh": "Tiếng Anh",
    "ly": "Vật lí",
    "hoa": "Hóa học",
    "sinh": "Sinh học",
    "su": "Lịch sử",
    "dia": "Địa lí",
    "gdkt": "GD KTPL",
    "tin": "Tin học",
    "congnghe": "Công nghệ",
    "nhac": "Âm nhạc",
    "mythuat": "Mĩ thuật"
}

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    scores = None
    ai_analysis = None
    history = session.get("history", [])

    if request.method == "POST":
        scores = {}

        for key in subjects:
            value = request.form.get(key)
            if value and value.strip():
                try:
                    scores[subjects[key]] = float(value.replace(",", "."))
                except:
                    pass

        if scores:
            avg = round(sum(scores.values()) / len(scores), 2)

            if avg >= 8:
                level = "GIỎI"
            elif avg >= 6.5:
                level = "KHÁ"
            elif avg >= 5:
                level = "TRUNG BÌNH"
            else:
                level = "YẾU"

            result = f"Điểm TB: {avg} | Học lực: {level}"
            session["scores"] = scores

            # ===== LƯU LỊCH SỬ =====
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            history.append({
                "time": now,
                "average": avg
            })
            session["history"] = history

            # ===== PHÂN LOẠI =====
            strong = [s for s,v in scores.items() if v >= 8]
            weak = [s for s,v in scores.items() if v < 5]

            if GROQ_API_KEY:
                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }

                prompt = f"""
                Môn mạnh: {strong}
                Môn yếu: {weak}

                Viết HTML theo cấu trúc:

                <h3><i class="fa-solid fa-brain"></i> Phân tích tư duy tổng thể</h3>
                <p>...</p>

                <h3><i class="fa-solid fa-star"></i> Điểm mạnh nổi bật</h3>
                <ul><li>...</li></ul>

                <h3><i class="fa-solid fa-chart-line"></i> Cải thiện và phát triển</h3>
                <p>...</p>

                <h3><i class="fa-solid fa-bullseye"></i> Nghề nghiệp phù hợp</h3>
                <p>...</p>

                Không dùng emoji.
                """

                payload = {
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": "Bạn là chuyên gia hướng nghiệp."},
                        {"role": "user", "content": prompt}
                    ]
                }

                try:
                    response = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    data = response.json()
                    ai_analysis = data["choices"][0]["message"]["content"]

                    # ===== LỌC RÁC AI TRẢ VỀ =====
                    ai_analysis = ai_analysis.replace("```html", "")
                    ai_analysis = ai_analysis.replace("```", "")
                    ai_analysis = ai_analysis.replace("Dưới đây là mã HTML theo cấu trúc yêu cầu:", "")
                    ai_analysis = ai_analysis.strip()
                except:
                    ai_analysis = "Lỗi AI."

    return render_template(
        "index.html",
        result=result,
        scores=scores,
        ai_analysis=ai_analysis,
        history=history
    )


@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    scores = session.get("scores")

    if not scores:
        return jsonify({"reply": "Hãy nhập điểm trước nhé!"})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": f"Điểm học sinh: {scores}"},
            {"role": "user", "content": user_msg}
        ]
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload
    )

    data = response.json()
    reply = data["choices"][0]["message"]["content"]

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)