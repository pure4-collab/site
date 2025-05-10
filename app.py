from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

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
            
        def get_address_id():
            p = soup.select_one(".top-block .left p")
            if not p: return None
            txt = p.get_text(strip=True)
            parts = txt.split(":",1)
            return parts[1].strip() if len(parts)>1 else None
            
        data = {
            "address_id":     get_address_id(),
            "joined_date":    get_text(".joined span"),
            "promo_link":     get_text("#copyLink"),
            "team_deposits":  get_text(".team span"),
            "referrals":      get_text(".ref .num span"),
            "sponsor":        get_text(".sponsor span"),
            "mining_balance": get_text(".block:nth-child(1) .summ.text-r"),
            "current_balance":get_text(".block:nth-child(2) .summ.text-r"),
            "daily_roi":      get_text(".roi"),
            "ref_rewards":    get_text(".rewards"),
            "total_payouts":  get_text(".block:nth-child(3) .summ.text-r"),
            "payout_queue":   get_text(".block:nth-child(3) .bottom-block span"),
            "deposits":       get_formatted_items(".left .list p", "Deposited"),
            "withdrawals":    get_formatted_items(".right .list p", "Payment made"),
            "source":         url
        }

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/deposit_address")
def gerar_endereco_deposito():
    wallet = request.args.get("wallet")
    if not wallet:
        return jsonify({"error": "Carteira não informada"}), 400

    try:
        session = requests.Session()
        session.headers.update({
            "Referer": f"https://pure3.cloud/report/{wallet}",
            "User-Agent": "Mozilla/5.0"
        })
        session.get(f"https://pure3.cloud/report/{wallet}")
        res = session.post("https://pure3.cloud/ajax/index.php", data={
            "endpoint": "offset",
            "w": "1329",
            "h": "1174"
        })

        soup = BeautifulSoup(res.text, "html.parser")
        address   = soup.select_one(".place_for_address")
        countdown = soup.select_one(".clock")
        min_start = soup.find("p", class_="min")

        return jsonify({
            "address":   address.text.strip() if address else None,
            "min_start": min_start.text.strip() if min_start else None,
            "timer":     countdown.text.strip() if countdown else None
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
