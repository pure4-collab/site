from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)  # <-- ESSA LINHA TEM QUE VIR ANTES DAS ROTAS

@app.route('/')
def home():
    return render_template('index.html')
  
@app.route('/api/relatorio', methods=['GET'])
def pegar_dados():
    wallet = request.args.get('wallet')
    if not wallet:
        return jsonify({"error": "Wallet address not provided"}), 400

    url = f"https://pure3.cloud/report/{wallet}"
    headers = { "User-Agent": "Mozilla/5.0" }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

        dados = {}

        def safe_extract(label):
            el = soup.find(text=label)
            return el.find_next("span").text.strip() if el else None

        dados['current_balance'] = safe_extract("Current Balance")
        dados['daily_roi'] = safe_extract("Today's ROI")
        dados['total_payouts'] = safe_extract("Payouts")
        dados['source'] = url

        return jsonify(dados)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
