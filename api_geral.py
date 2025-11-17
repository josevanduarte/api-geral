
from flask import Flask, request, jsonify
import hashlib
import requests
from datetime import datetime

app = Flask(__name__)

TOKEN_ORIGINAL = "mRvd11QSxXs5LUL$CfW1"
USER = "02297349289"
API_URL = "https://stou.ifractal.com.br/i9saude/rest/"

def gerar_token_sha256(data_formatada):
    token_concatenado = TOKEN_ORIGINAL + data_formatada
    return hashlib.sha256(token_concatenado.encode()).hexdigest()

def get_headers():
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    return {
        "Content-Type": "application/json",
        "User": USER,
        "Token": gerar_token_sha256(data_hoje)
    }

@app.route("/")
def home():
    return "✅ API Geral online! Use /ponto_geral ou /horas_extras com parâmetros."

@app.route("/ponto_geral", methods=["GET"])
def ponto_geral():
    body = {
        "pag": "ponto_geral",
        "cmd": "get"
    }
    # Adiciona filtros da URL se existirem
    for key in request.args:
        body[key] = request.args.get(key)

    try:
        response = requests.post(API_URL, json=body, headers=get_headers())
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/horas_extras", methods=["GET"])
def horas_extras():
    dtde = request.args.get("inicio")
    dtate = request.args.get("fim")

    if not dtde or not dtate:
        return jsonify({"erro": "Parâmetros 'inicio' e 'fim' são obrigatórios."}), 400

    body = {
        "pag": "ponto_relatorio_hora_extra",
        "cmd": "get",
        "dtde": dtde,
        "dtate": dtate
    }

    try:
        response = requests.post(API_URL, json=body, headers=get_headers())
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
