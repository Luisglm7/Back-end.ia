# app.py - Gerador de Histórias com IA

# Imports necessários
from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
import os
from dotenv import load_dotenv
import json

# Carrega variáveis de ambiente
load_dotenv()

# Cria a aplicação Flask
app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Configuração do cliente Gemini
API_KEY = os.getenv("API_KEY")
client = genai.Client(api_key=API_KEY)

def gerar_historia(tema, genero="fantasia", extensao="media"):
    """
    Gera uma história com base nos parâmetros fornecidos
    
    Args:
        tema (str): Tema principal da história
        genero (str): Gênero da história (fantasia, ficção, aventura, etc.)
        extensao (str): 'curta', 'media' ou 'longa'
    """
    # Define o tamanho com base na extensão
    tamanhos = {
        "curta": "uma história curta de 100-150 palavras",
        "media": "uma história média de 200-300 palavras", 
        "longa": "uma história longa de 400-500 palavras"
    }
    
    prompt = f"""
        Crie {tamanhos.get(extensao, 'uma história média')} no gênero {genero} com o tema: {tema}.
        A história deve ter:
        - Um título criativo
        - Personagens interessantes
        - Um conflito ou desafio
        - Um desfecho satisfatório
        - Opcionalmente uma moral ou lição
        
        Se o tema for inapropriado, retorne uma mensagem educada sobre criar histórias positivas.
        
        Formato de resposta em JSON:
        {{
            "titulo": "Título da história",
            "tema": "Tema solicitado",
            "genero": "Gênero literário",
            "extensao": "Duração da história",
            "personagens": [
                "Nome e breve descrição do personagem principal",
                "Outros personagens relevantes"
            ],
            "historia": [
                "Parágrafo 1 - Introdução",
                "Parágrafo 2 - Desenvolvimento",
                "Parágrafo 3 - Conclusão"
            ],
            "moral": "Moral da história (opcional)"
        }}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
            }
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Erro ao gerar história: {e}")
        return {
            "erro": "Não foi possível gerar a história",
            "detalhes": str(e)
        }

@app.route('/historia', methods=['POST'])
def criar_historia():
    try:
        dados = request.get_json()
        
        # Validação básica
        if not dados or not isinstance(dados, dict):
            return jsonify({'erro': 'Requisição inválida. Envie um JSON válido.'}), 400
            
        tema = dados.get('tema', '').strip()
        if len(tema) < 3:
            return jsonify({'erro': 'O tema deve ter pelo menos 3 caracteres.'}), 400
            
        genero = dados.get('genero', 'fantasia')
        extensao = dados.get('extensao', 'media')
        
        # Gera a história
        historia = gerar_historia(tema, genero, extensao)
        
        if 'erro' in historia:
            return jsonify(historia), 500
            
        return jsonify(historia), 200
        
    except Exception as e:
        print(f"Erro no servidor: {e}")
        return jsonify({
            'erro': 'Erro interno no servidor',
            'detalhes': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)