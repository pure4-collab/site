
from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup

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

        saldo_atual = soup.find(text="Current Balance").find_next("span").text.strip()
        lucro_diario = soup.find(text="Today's ROI").find_next("span").text.strip()
        total_payouts = soup.find(text="Payouts").find_next("span").text.strip()

        dados['current_balance'] = saldo_atual
        dados['daily_roi'] = lucro_diario
        dados['total_payouts'] = total_payouts
        dados['source'] = url

        return jsonify(dados)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
