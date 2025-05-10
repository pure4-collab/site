
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

        def get_list_items(selector):
            items = soup.select(selector)
            return [i.get_text(strip=True) for i in items] if items else []

        data = {
            "address_id": get_text(".left p span"),  # My Address ID
            "joined_date": get_text(".joined span"),  # Joined
            "promo_link": get_text("#copyLink"),  # My Promo-Link
            "team_deposits": get_text(".team span"),  # Team Deposits
            "referrals": get_text(".ref .num span"),  # Referrals
            "sponsor": get_text(".sponsor span"),  # Sponsor
            "mining_balance": get_text(".block:nth-child(1) .summ.text-r"),  # Mining Balance
            "current_balance": get_text(".block:nth-child(2) .summ.text-r"),  # Current Balance
            "daily_roi": get_text(".roi"),  # ROI Today
            "ref_rewards": get_text(".rewards"),  # Ref Rewards
            "total_payouts": get_text(".block:nth-child(3) .summ.text-r"),  # Payouts
            "payout_queue": get_text(".block:nth-child(3) .bottom-block span"),  # queue
            "deposits": get_list_items(".left .list p"),  # My Deposits
            "withdrawals": get_list_items(".right .list p"),  # My Withdrawals
            "source": url
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
