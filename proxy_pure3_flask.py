from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/relatorio', methods=['GET'])
def pegar_dados():
    wallet = request.args.get('wallet')
    if not wallet:
        return jsonify({"error": "Wallet address not provided"}), 400

    url = f"https://pure3.cloud/report/{wallet}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

        dados = {}

        # Current Balance (pega o primeiro valor com classe 'summ text-r')
        current_balance_tag = soup.find("p", class_="summ text-r")
        dados['current_balance'] = current_balance_tag.text.strip() if current_balance_tag else None

        # ROI Hoje (pega o <p class="roi"> e extrai os valores de texto)
        roi_tag = soup.find("p", class_="roi")
        if roi_tag:
            roi_text = roi_tag.get_text(strip=True)
            dados['daily_roi'] = roi_text.replace("Today's ROI:", "").strip()
        else:
            dados['daily_roi'] = None

        # Ref Rewards (pega o texto do <p class="rewards">)
        ref_tag = soup.find("p", class_="rewards")
        if ref_tag:
            ref_text = ref_tag.get_text(strip=True)
            dados['ref_rewards'] = ref_text.replace("Ref Rewards:", "").strip()
        else:
            dados['ref_rewards'] = None

        # Total Payouts (mantemos do método anterior)
        payout_label = soup.find(text="Payouts")
        if payout_label:
            payout_value = payout_label.find_next("span").text.strip()
            dados['total_payouts'] = payout_value
        else:
            dados['total_payouts'] = None

        dados['source'] = url
        return jsonify(dados)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Executa no ambiente Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
