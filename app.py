from flask import Flask, render_template, request, jsonify
import requests

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
    "gdkt": "GD KTPL",
    "tin": "Tin học",
    "congnghe": "Công nghệ",
    "nhac": "Âm nhạc",
    "mythuat": "Mĩ thuật"
}

@app.route("/", methods=["GET","POST"])
def home():
    result=None
    scores=None

    if request.method=="POST":
        scores={}
        for key in subjects:
            v=request.form.get(key)
            if v and v.strip():
                try:
                    scores[subjects[key]]=float(v.replace(",","."))
                except:
                    pass

        if scores:
            avg=sum(scores.values())/len(scores)

            if avg>=8: level="Học lực GIỎI"
            elif avg>=6.5: level="Học lực KHÁ"
            elif avg>=5: level="Học lực TRUNG BÌNH"
            else: level="Học lực YẾU"

            weak=[s for s,v in scores.items() if v<5]

            natural=["Toán","Vật lí","Hóa học","Sinh học","Tin học","Công nghệ"]
            social=["Ngữ văn","Lịch sử","Địa lí","GD KTPL"]

            nat=[scores[s] for s in scores if s in natural]
            soc=[scores[s] for s in scores if s in social]

            nat_avg=sum(nat)/len(nat) if nat else 0
            soc_avg=sum(soc)/len(soc) if soc else 0

            if nat_avg>soc_avg+1:
                orientation="Bạn thiên về KHỐI TỰ NHIÊN"
            elif soc_avg>nat_avg+1:
                orientation="Bạn thiên về KHỐI XÃ HỘI"
            else:
                orientation="Bạn học khá CÂN BẰNG"

            result=f"""
            Điểm TB: {round(avg,2)} <br>
            {level}<br><br>
            {orientation}<br>
            """

            if weak:
                result+= "Cần cải thiện: "+", ".join(weak)

    return render_template("index.html",result=result,scores=scores)


# ===== CHAT AI =====
@app.route("/chat",methods=["POST"])
def chat():
    msg=request.form.get("message","")

    try:
        r=requests.post("http://localhost:11434/api/generate",
        json={
            "model":"llama3",
            "prompt":f"Bạn là trợ lý định hướng học sinh Việt Nam. Trả lời ngắn gọn bằng tiếng Việt.\nCâu hỏi: {msg}",
            "stream":False
        })

        data=r.json()
        reply=data.get("response","AI chưa trả lời")
        return jsonify({"reply":reply})

    except:
        return jsonify({"reply":"⚠️ AI chưa chạy. Hãy bật ollama serve"})


if __name__=="__main__":
    app.run(debug=True)