from flask import Flask, request, jsonify
import hashlib
import requests
from datetime import datetime

app = Flask(__name__)

# Configurações da API
TOKEN_ORIGINAL = "mRvd11QSxXs5LUL$CfW1"  # Seu token original
USER_LOGIN = "02297349289"  # Seu user-login
API_URL = "https://stou.ifractal.com.br/i9saude/rest/"

def gerar_token_sha256(data_formatada):
    """
    Gera token SHA256 conforme documentação:
    Token original + data atual (dd/mm/aaaa) → SHA256
    """
    token_concatenado = TOKEN_ORIGINAL + data_formatada
    return hashlib.sha256(token_concatenado.encode()).hexdigest()

def converter_boolean(valor):
    """Converte string para boolean"""
    if isinstance(valor, str):
        return valor.lower() in ['true', '1', 'sim', 's', 'yes']
    return bool(valor)

def converter_integer(valor):
    """Converte string para integer"""
    try:
        return int(valor) if valor else None
    except ValueError:
        return None

@app.route("/")
def home():
    return """
    ✅ API Ponto Geral está online!
    
    📋 Endpoint: GET /ponto_geral
    
    🔧 Filtros disponíveis:
    • calcular_saldo_acumulado (boolean)
    • dtde (date) - formato: DD/MM/YYYY
    • dtate (date) - formato: DD/MM/YYYY  
    • cod_pessoa (integer) - Funcionário
    • cod_empresa (integer) - Empresa
    • cod_unidade (integer) - Departamento
    • cod_centro_custo (integer) - Centro de Custo
    • cod_cargo (integer) - Cargo
    • divergencia (string) - Divergência
    • cod_hierarquia (integer) - Hierarquia
    • vinculado_periodo (boolean) - Vinculado no período
    • maior_que (integer) - Maior que
    • menor_que (integer) - Menor que
    • apenas_ativos (boolean) - Apenas Ativos
    
    📝 Exemplo: /ponto_geral?dtde=20/07/2025&dtate=19/08/2025&divergencia=&maior_que=9
    """

@app.route("/ponto_geral", methods=["GET"])
def consultar_ponto_geral():
    # Gera token conforme documentação
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    token_criptografado = gerar_token_sha256(data_hoje)

    # Headers conforme documentação
    headers = {
        "Content-Type": "application/json",
        "User": USER_LOGIN,
        "Token": token_criptografado
    }

    # Body básico obrigatório
    body = {
        "pag": "ponto_geral",
        "cmd": "get"
    }
    
    # Campos de filtro opcionais
    filtros = {}
    
    # Booleans
    if request.args.get("calcular_saldo_acumulado") is not None:
        filtros["calcular_saldo_acumulado"] = converter_boolean(request.args.get("calcular_saldo_acumulado"))
    
    if request.args.get("vinculado_periodo") is not None:
        filtros["vinculado_periodo"] = converter_boolean(request.args.get("vinculado_periodo"))
    
    if request.args.get("apenas_ativos") is not None:
        filtros["apenas_ativos"] = converter_boolean(request.args.get("apenas_ativos"))
    
    # Datas
    if request.args.get("dtde"):
        filtros["dtde"] = request.args.get("dtde")
    if request.args.get("dtate"):
        filtros["dtate"] = request.args.get("dtate")
    
    # String
    if request.args.get("divergencia") is not None:  # Permite string vazia
        filtros["divergencia"] = request.args.get("divergencia")
    
    # Integers
    campos_integer = [
        "cod_pessoa", "cod_empresa", "cod_unidade", 
        "cod_centro_custo", "cod_cargo", "cod_hierarquia",
        "maior_que", "menor_que"
    ]
    
    for campo in campos_integer:
        if request.args.get(campo):
            valor = converter_integer(request.args.get(campo))
            if valor is not None:
                filtros[campo] = valor
    
    # Adiciona filtros ao body se existirem
    if filtros:
        body.update(filtros)

    try:
        response = requests.post(API_URL, json=body, headers=headers)
        
        # Log para debug
        print(f"📤 Body enviado: {body}")
        print(f"🔑 Token gerado: {token_criptografado[:20]}...")
        print(f"📅 Data usada: {data_hoje}")
        print(f"📥 Status da resposta: {response.status_code}")
        
        return jsonify(response.json())
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            "erro": "Erro na comunicação com a API",
            "detalhes": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "erro": "Erro interno do servidor", 
            "detalhes": str(e)
        }), 500

@app.route("/debug", methods=["GET"])
def debug_endpoint():
    """Endpoint para visualizar o que seria enviado sem fazer a chamada real"""
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    token_criptografado = gerar_token_sha256(data_hoje)
    
    # Processa todos os parâmetros da mesma forma que o endpoint principal
    body = {"pag": "ponto_geral", "cmd": "get"}
    filtros = {}
    
    # Booleans
    if request.args.get("calcular_saldo_acumulado") is not None:
        filtros["calcular_saldo_acumulado"] = converter_boolean(request.args.get("calcular_saldo_acumulado"))
    if request.args.get("vinculado_periodo") is not None:
        filtros["vinculado_periodo"] = converter_boolean(request.args.get("vinculado_periodo"))
    if request.args.get("apenas_ativos") is not None:
        filtros["apenas_ativos"] = converter_boolean(request.args.get("apenas_ativos"))
    
    # Datas
    if request.args.get("dtde"):
        filtros["dtde"] = request.args.get("dtde")
    if request.args.get("dtate"):
        filtros["dtate"] = request.args.get("dtate")
    
    # String (permite vazia)
    if request.args.get("divergencia") is not None:
        filtros["divergencia"] = request.args.get("divergencia")
    
    # Integers
    campos_integer = [
        "cod_pessoa", "cod_empresa", "cod_unidade", 
        "cod_centro_custo", "cod_cargo", "cod_hierarquia",
        "maior_que", "menor_que"
    ]
    
    for campo in campos_integer:
        if request.args.get(campo):
            valor = converter_integer(request.args.get(campo))
            if valor is not None:
                filtros[campo] = valor
    
    if filtros:
        body.update(filtros)
    
    return jsonify({
        "info": "🐛 DEBUG - Não faz chamada real para API",
        "configuracao": {
            "api_url": API_URL,
            "user_login": USER_LOGIN,
            "token_original": f"{TOKEN_ORIGINAL[:5]}...",
            "data_atual": data_hoje,
            "token_exemplo_concatenacao": f"{TOKEN_ORIGINAL}{data_hoje}",
            "token_sha256_gerado": f"{token_criptografado[:20]}..."
        },
        "parametros_recebidos": dict(request.args),
        "headers_que_seriam_enviados": {
            "Content-Type": "application/json",
            "User": USER_LOGIN,
            "Token": f"{token_criptografado[:20]}..."
        },
        "body_que_seria_enviado": body,
        "total_filtros_aplicados": len(filtros)
    })

@app.route("/exemplo-documentacao", methods=["GET"])
def exemplo_da_documentacao():
    """Reproduz exatamente o exemplo da documentação"""
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    token_criptografado = gerar_token_sha256(data_hoje)
    
    headers = {
        "Content-Type": "application/json",
        "User": USER_LOGIN,
        "Token": token_criptografado
    }
    
    # Exemplo exato da documentação
    body = {
        "pag": "ponto_geral",
        "cmd": "get",
        "dtde": "20/07/2025",
        "dtate": "19/08/2025", 
        "divergencia": "",
        "maior_que": 9
    }
    
    try:
        response = requests.post(API_URL, json=body, headers=headers)
        print(f"📋 Exemplo da documentação executado")
        print(f"📤 Body: {body}")
        print(f"📥 Status: {response.status_code}")
        
        return jsonify({
            "info": "Exemplo da documentação executado",
            "body_enviado": body,
            "resposta": response.json()
        })
    except Exception as e:
        return jsonify({
            "erro": "Erro ao executar exemplo da documentação",
            "detalhes": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)