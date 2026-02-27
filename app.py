from flask import Flask, render_template, request
import time

app = Flask(__name__)

subjects = {
    "toan": "Toán",
    "van": "Ngữ văn",
    "anh": "Tiếng Anh",
    "ly": "Vật lí",
    "hoa": "Hóa học",
    "sinh": "Sinh học",
    "su": "Lịch sử",
    "dia": "Địa lí",
    "gdkt": "GD Kinh tế & PL",
    "tin": "Tin học",
    "congnghe": "Công nghệ",
    "nhac": "Âm nhạc",
    "mythuat": "Mĩ thuật"
}

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    scores = {}

    if request.method == "POST":
        time.sleep(2) #giả lập AI suy nghĩ

        for key in subjects:
            value = request.form.get(key)

            if value and value.strip():
                try:
                    clean_value = value.strip().replace(",", ".")
                    scores[subjects[key]] = float(clean_value)
                except:
                    pass

        if scores:
            avg = sum(scores.values()) / len(scores)

            if avg >= 8:
                level = "Học lực GIỎI"
            elif avg >= 6.5:
                level = "Học lực KHÁ"
            elif avg >= 5:
                level = "Học lực TRUNG BÌNH"
            else:
                level = "Học lực YẾU"

            # tìm môn yếu nhất
            weakest = min(scores, key=scores.get)
            weakest_score = scores[weakest]

            if weakest_score < 7:
                new_scores = scores.copy()
                new_scores[weakest] = 7
                future_avg = sum(new_scores.values()) / len(new_scores)

                improve_msg = f"""
                📈 Nếu bạn nâng <b>{weakest}</b> từ {weakest_score} → 7<br>
                Điểm TB sẽ tăng từ <b>{round(avg,2)}</b> → <b>{round(future_avg,2)}</b>
                """
            else:
                improve_msg = "Bạn không có môn yếu cần cải thiện!"

            weak_subjects = [s for s, sc in scores.items() if sc < 5]

            natural = ["Toán","Vật lí","Hóa học","Sinh học","Tin học","Công nghệ"]
            social = ["Ngữ văn","Lịch sử","Địa lí","GD Kinh tế & PL"]

            nat_scores = [scores[s] for s in scores if s in natural]
            soc_scores = [scores[s] for s in scores if s in social]

            nat_avg = sum(nat_scores)/len(nat_scores) if nat_scores else 0
            soc_avg = sum(soc_scores)/len(soc_scores) if soc_scores else 0

            if nat_avg > soc_avg + 1:
                orientation = "Bạn thiên về KHỐI TỰ NHIÊN."
                career = "Gợi ý: CNTT, kỹ thuật, AI, khoa học dữ liệu."
            elif soc_avg > nat_avg + 1:
                orientation = "Bạn thiên về KHỐI XÃ HỘI."
                career = "Gợi ý: luật, marketing, kinh tế, truyền thông."
            else:
                orientation = "Bạn học khá CÂN BẰNG."
                career = "Bạn phù hợp nhiều ngành liên ngành."

            if weak_subjects:
                advice = "Bạn cần cải thiện: " + ", ".join(weak_subjects)
            else:
                advice = "Không có môn yếu rõ rệt."

            result = f"""
            Điểm trung bình: {round(avg,2)} <br>
            {level} <br><br>
            {improve_msg}<br><br>
            <b>Phân tích:</b><br>
            {orientation}<br>
            {career}<br><br>
            {advice}
            """
        else:
            result = "Bạn chưa nhập môn nào"

    return render_template("index.html", result=result, scores=scores)

if __name__ == "__main__":
    app.run(debug=True)