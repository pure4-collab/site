
from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/painel")
def painel():
    return render_template("panel.html")

@app.route("/api/relatorio")
def api_relatorio():
    wallet = request.args.get("wallet")
    if not wallet:
        return jsonify({"error": "Carteira não fornecida"}), 400

    try:
        url = f"https://pure3.cloud/report/{wallet}"
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        def get_text(selector):
            tag = soup.select_one(selector)
            return tag.get_text(strip=True) if tag else None

        data = {
            "current_balance": get_text(".block:nth-child(2) .summ.text-r"),
            "daily_roi": get_text(".roi"),
            "ref_rewards": get_text(".rewards"),
            "total_payouts": get_text(".block:nth-child(3) .summ.text-r"),
            "source": url
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
