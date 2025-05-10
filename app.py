from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

# Inicializa o Flask
app = Flask(__name__)

# Rota da página inicial
@app.route("/")
def home():
    return render_template("index.html")

# Rota do painel de usuário
@app.route("/painel")
def painel():
    return render_template("panel.html")

# API que retorna todos os dados do relatório
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

        def get_formatted_items(selector, is_withdrawal=False):
            items = soup.select(selector)
            result = []
            for i in items:
                text = i.get_text(strip=True)
                span_trx = i.select_one("span")
                a_tag    = i.select_one("a")
                date_part = text.split(" - ")[0]

                if not is_withdrawal and "Deposited:" in text:
                    # Depósitos: "Apr 21, 10:06 - Deposited: 704.179317 TRX / $185.34 - e497c***e5a8a"
                    trx = span_trx.get_text(strip=True) if span_trx else ""
                    usd_match = re.search(r"/\s*(\$[\d\.]+)", text)
                    usd = usd_match.group(1) if usd_match else ""
                    hash_text = a_tag.text if a_tag else ""
                    link = a_tag["href"] if a_tag else ""
                    result.append(
                        f'<p>{date_part} - Deposited: <span>{trx}</span> / {usd} - '
                        + (f'<a href="{link}" target="_blank">{hash_text}</a>' if a_tag else hash_text)
                        + "</p>"
                    )
                else:
                    # Saques: "May 09, 21:24 - Payment made: 40.735022 TRX / $10.6 - In queue" ou com link
                    trx = span_trx.get_text(strip=True) if span_trx else ""
                    usd_match = re.search(r"/\s*(\$[\d\.]+)", text)
                    usd = usd_match.group(1) if usd_match else ""
                    if a_tag:
                        hash_text = a_tag.text
                        link = a_tag["href"]
                        result.append(
                            f'<p>{date_part} - Payment made: <span>{trx}</span> / {usd} - '
                            f'<a href="{link}" target="_blank">{hash_text}</a></p>'
                        )
                    else:
                        status = text.split(" - ")[-1]
                        result.append(
                            f'<p>{date_part} - Payment made: <span>{trx}</span> / {usd} - {status}</p>'
                        )
            return result

        data = {
            "address_id":     get_text(".left p:nth-of-type(2)"),
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
            "deposits":       get_formatted_items(".left .list p", is_withdrawal=False),
            "withdrawals":    get_formatted_items(".right .list p", is_withdrawal=True),
            "source":         url
        }

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API para gerar endereço de depósito
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
        address = soup.select_one(".place_for_address")
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
