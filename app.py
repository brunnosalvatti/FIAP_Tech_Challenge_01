from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
import requests
import pandas as pd

app = Flask(__name__)
app.config.from_object("config")
db = SQLAlchemy(app)
Swagger(app)
jwt = JWTManager(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Banco de Dados Criado")

df = pd.read_csv("data/web_scraping.csv", sep=",")
url = "https://books.toscrape.com/"


@app.route("/api/v1/auth/register", methods=["POST"])
def register():
    """
    Registro de usuário
    ---
    tags:
      - Registro
    description: Endpoint para registrar um novo usuário. Envie um JSON com 'username' e 'password'.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - username
              - password
            properties:
              username:
                type: string
              password:
                type: string
    responses:
      201:
        description: Usuário criado com sucesso
      400:
        description: Usuário já existe ou parâmetros inválidos
    """
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Parâmetros ausentes ou inválidos"}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "User already exists"}), 400

    new_user = User(username=data["username"], password=data["password"])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201


@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    """
    Login de usuário
    ---
    tags:
      - Login
    description: Endpoint para realizar um login e receber um token. Envie um JSON com 'username' e 'password'.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - username
              - password
    responses:
      200:
        description: Login realizado
      400:
        description: Login inválido
    """
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Parâmetros ausentes ou inválidos"}), 400

    user = User.query.filter_by(username=data["username"]).first()
    if user and user.password == data["password"]:
        token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": token}), 200

    return jsonify({"error": "invalid credentials"}), 401


@app.route("/api/v1/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Renovação de Token
    ---
    tags:
      - Autenticação
    summary: Renova o token de acesso
    description: >
      Endpoint para renovar o token de acesso utilizando um **refresh token** válido.  
      O refresh token deve ser enviado no **header Authorization** no formato `Bearer <token>`.
    security:
      - BearerAuth: []
    responses:
      200:
        description: Novo token de acesso gerado com sucesso
        schema:
          type: object
          properties:
            access_token:
              type: string
              description: Novo token JWT de acesso
              example: "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
      401:
        description: Token de refresh inválido ou expirado
    """
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token), 200


@app.route("/api/v1/scraping/trigger", methods=["POST"])
@jwt_required()
def protected():
    """
    Área Restrita
    ---
    tags:
      - Acesso Restrito
    description: Endpoint protegido que requer token JWT válido no header Authorization para acesso.
    security:
      - BearerAuth: []
    responses:
      200:
        description: Acesso autorizado. Retorna mensagem com ID do usuário.
      401:
        description: Token ausente ou inválido.
    """
    current_user_id = get_jwt_identity()
    return jsonify(
        {"mensage": f"Usuário com ID {current_user_id} Acessou a Rota Protegida"}
    )

@app.route("/api/v1/books")
def books():
    """
    Lista de livros
    ---
    tags:
      - Livros Disponíveis
    description: Retorna uma lista com os títulos de todos os livros disponíveis na base de dados.
    responses:
      200:
        description: Lista de títulos dos livros
        schema:
          type: array
          items:
            type: string
    """
    return jsonify(df["Title"].tolist()), 200

@app.route("/api/v1/books/<id>")
def books_id(id):
    """
    Detalhes de um livro
    ---
    tags:
      - Livros Disponíveis
    description: Retorna as informações completas de um livro a partir de seu ID na base de dados.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do livro na base de dados
    responses:
      200:
        description: Dados do livro
        schema:
          type: array
          items:
            type: object
      404:
        description: Livro não encontrado
    """
    id = int(id)
    book_id = df.query("Index == @id")
    book_id = book_id.to_dict(orient="records")
    return jsonify(book_id)

@app.route("/api/v1/books/search")
def search():
    """
    Busca de livros
    ---
    tags:
      - Livros Disponíveis
    description: Busca livros na base de dados filtrando por título e/ou categoria.
    parameters:
      - name: title
        in: query
        type: string
        required: false
        description: Parte ou nome completo do título do livro.
      - name: category
        in: query
        type: string
        required: false
        description: Parte ou nome completo da categoria do livro.
    responses:
      200:
        description: Lista de livros que correspondem aos critérios de busca.
        schema:
          type: array
          items:
            type: object
    """
    title = request.args.get("title", "")
    category = request.args.get("category", "")
    df_filtered = df
    if title:
        df_filtered = df_filtered[
            df_filtered["Title"].str.contains(title, case=False, na=False)
        ]
    if category:
        df_filtered = df_filtered[
            df_filtered["Category"].str.contains(category, case=False, na=False)
        ]
    return jsonify(df_filtered.to_dict(orient="records"))

@app.route("/api/v1/categories")
def categories():
    """
    Lista de categorias
    ---
    tags:
      - Categorias
    description: Retorna a lista de todas as categorias únicas presentes na base de dados.
    responses:
      200:
        description: Lista de categorias únicas
        schema:
          type: array
          items:
            type: string
    """
    categories = df.iloc[:, 1]
    unique_categories = list(set(categories))
    return jsonify(unique_categories)

@app.route("/api/v1/health")
def health():
    """
    Verificação de saúde da API
    ---
    tags:
      - Monitoramento
    description: Verifica a conectividade da API com o serviço externo configurado.
    responses:
      200:
        description: Conexão bem-sucedida com o serviço externo.
        schema:
          type: object
          properties:
            status:
              type: string
              description: Estado da conexão.
            code:
              type: integer
              description: Código HTTP retornado pelo serviço externo.
      400:
        description: Falha na conexão com o serviço externo.
        schema:
          type: object
          properties:
            status:
              type: string
              description: Estado da conexão.
            code:
              type: integer
              description: Código HTTP retornado ou ausência de resposta.
    """
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return jsonify({"status": "conectado", "code": 200}), 200
        else:
            return jsonify({"status": "falha", "code": response.status_code}), 400
    except requests.RequestException:
        return jsonify({"status": "erro de conexão"}), 400


@app.route("/api/v1/stats/overview")
def overview():
    """
    Estatísticas gerais dos livros
    ---
    tags:
      - Estatísticas
    description: Retorna um resumo com estatísticas gerais dos livros disponíveis na base de dados.
    responses:
      200:
        description: Resumo estatístico dos livros.
        schema:
          type: object
          properties:
            Stock:
              type: integer
              description: Quantidade total de livros em estoque.
            Average Rating:
              type: number
              format: float
              description: Média das avaliações dos livros.
            Average Price:
              type: number
              format: float
              description: Preço médio dos livros.
            Number of Books:
              type: integer
              description: Número total de livros cadastrados.
    """
    df["Price"] = pd.to_numeric(df["Price"])
    df["Stock"] = pd.to_numeric(df["Stock"])
    df["Rating"] = pd.to_numeric(df["Rating"])

    num_livros = len(df["Title"].tolist())
    average_price = round(df["Price"].mean(), 2)
    average_rating = df["Rating"].mean()
    stock = df["Stock"].sum()

    overview = {
        "Stock": int(stock),
        "Average Rating": float(round(average_rating, 2)),
        "Average Price": float(average_price),
        "Number of Books": num_livros,
    }
    return jsonify(overview)

@app.route("/api/v1/stats/categories")
def stats_categories():
    """
    Estatísticas por categoria
    ---
    tags:
      - Estatísticas
    description: Retorna o número de livros e a média das avaliações agrupados por categoria.
    responses:
      200:
        description: Estatísticas agrupadas por categoria.
        schema:
          type: array
          items:
            type: object
            properties:
              Category:
                type: string
                description: Nome da categoria
              Number_of_Books:
                type: integer
                description: Quantidade de livros na categoria
              Avg_Rating:
                type: number
                format: float
                description: Avaliação média dos livros da categoria
    """
    grouped = (
        df.groupby("Category")
        .agg(Number_of_Books=("Title", "count"), Avg_Rating=("Rating", "mean"))
        .reset_index()
    )
    return jsonify(grouped.to_dict(orient="records"))



@app.route("/api/v1/books/top-rated")
def top_rated():
    """
    Livros com avaliação máxima
    ---
    tags:
      - Livros Disponíveis
    description: Retorna a lista de livros com avaliação máxima (nota 5).
    responses:
      200:
        description: Lista de livros com nota 5.
        schema:
          type: array
          items:
            type: object
    """
    top_rated = df.query("Rating == 5")
    return jsonify(top_rated.to_dict(orient="records"))


@app.route("/api/v1/books/price-range")
def price_range():
    """
    Filtrar Livros por Faixa de Preço
    ---
    tags:
      - Consulta por Preço
    description: Retorna os livros cujo preço esteja dentro de uma faixa especificada.
    parameters:
      - name: min
        in: query
        type: number
        format: float
        required: false
        description: Preço mínimo.
      - name: max
        in: query
        type: number
        format: float
        required: false
        description: Preço máximo.
    responses:
      200:
        description: Lista de livros dentro da faixa de preço especificada.
        schema:
          type: array
          items:
            type: object
            properties:
              Index:
                type: integer
              Title:
                type: string
              Price:
                type: number
                format: float
              Category:
                type: string
              Rating:
                type: number
                format: float
              Stock:
                type: integer
    """
    min_val = request.args.get("min", None)
    max_val = request.args.get("max", None)

    try:
        min_val = float(min_val) if min_val is not None else None
    except ValueError:
        min_val = None

    try:
        max_val = float(max_val) if max_val is not None else None
    except ValueError:
        max_val = None

    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df_filtered = df

    if min_val is not None:
        df_filtered = df_filtered[df_filtered["Price"] >= min_val]
    if max_val is not None:
        df_filtered = df_filtered[df_filtered["Price"] <= max_val]

    return jsonify(df_filtered.to_dict(orient="records"))


if __name__ == "__main__":
    app.run(debug=True)
