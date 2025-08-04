from flask import Flask, request, jsonify, render_template       # Da biblioteca flask, importamos a classe Flask e os métodos requests, jsonify e render_template
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
import requests
import pandas as pd

app=Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
Swagger(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique = True, nullable = False)
    password = db.Column(db.String(120), nullable = False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Banco de Dados Criado")

df=pd.read_csv('data/web_scraping.csv', sep=',')                  # Abertura do arquivo gerado por web scraping 
url='https://books.toscrape.com/'                                 # URL base



@app.route('/')
def home():
    return f'bem vindo!'

# Endpoints obrigatórios

'''Lista todos os livros disponíveis na base de dados'''
@app.route('/api/v1/books')                                      # A partir da rota /api/v1/books, será usada uma função books 
def books(): 
    return jsonify(df['Title'].tolist())                         # Converte a coluna 'Title' no arquivo para um dado tipo lista e por fim retorna essa lista.
    


'''Retorna os detalhes completos de um livro'''
@app.route('/api/v1/books/<id>')
def books_id(id):
    id = int(id)  # Converte id para inteiro
    book_id = df.query('Index == @id')
    book_id = book_id.to_dict(orient='records')  # Converte para lista de dicionários
    return jsonify(book_id)


'''Busca livros por título e/ou categoria por meio de /api/v1/books/search?title={title}&category={category}.'''
@app.route('/api/v1/books/search')
def search():
    title = request.args.get('title', '')
    category = request.args.get('category', '')
    df_filtered = df
    if title:
        df_filtered = df_filtered[df_filtered['Title'].str.contains(title, case=False, na=False)]
    if category:
        df_filtered = df_filtered[df_filtered['Category'].str.contains(category, case=False, na=False)]
    return jsonify(df_filtered.to_dict(orient='records'))



'''Lista todas as categorias de livros disponíveis'''
@app.route('/api/v1/categories')
def categories():
    categories = df.iloc[:, 1]                 # Segunda coluna
    unique_categories = list(set(categories))  # Obtem Apenas as Categorias Únicas
    return jsonify(unique_categories)

    
'''Verifica o status da API e conectividade com os dados'''
@app.route('/api/v1/health')
def health():
    if requests.get(url).status_code==200:
        return 'A API possui conectividade via Request (Status Code = 200)'
    else:
        return 'A API não possui conectividade via Request (Status Code != 200)'















# Endpoints opicionais:

'''Estatísticas gerais da coleção (total de livros, preço médio, distribuição de ratings)'''
@app.route('/api/v1/stats/overview')
def overview():
    # Converte os campos para numéricos
    df['Price'] = pd.to_numeric(df['Price'])
    df['Stock'] = pd.to_numeric(df['Stock'])
    df['Rating'] = pd.to_numeric(df['Rating'])

    num_livros = len(df['Title'].tolist())
    average_price = round(df['Price'].mean(), 2)
    average_rating = df['Rating'].mean()
    stock = df['Stock'].sum()

    overview = {
        'Stock': int(stock),
        'Average Rating': float(round(average_rating, 2)),
        'Average Price': float(average_price),
        'Number of Books': num_livros
    }

    return jsonify(overview)

'''Retorna Atributos para Cada Categoria'''
@app.route('/api/v1/stats/categories')
def stats_categories():
    grouped = df.groupby('Category').agg(
        Number_of_Books = ('Title', 'count'),    # Quantidade de livros
        Avg_Rating = ('Rating', 'mean')           # Média do rating
    ).reset_index()

    return jsonify(grouped.to_dict(orient='records'))



'''Lista os livros com melhor avaliação (rating mais alto)'''
@app.route('/api/v1/books/top-rated')
def top_rated():
    top_rated = df.query("Rating == 5")
    return jsonify(top_rated.to_dict(orient='records'))


'''Filtra livros dentro de uma faixa de preço específica'''
@app.route('/api/v1/books/price-range')
def price_range():
    min_val = request.args.get('min', None)
    max_val = request.args.get('max', None)

    try:
        min_val = float(min_val) if min_val is not None else None
    except ValueError:
        min_val = None

    try:
        max_val = float(max_val) if max_val is not None else None
    except ValueError:
        max_val = None

    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df_filtered = df

    if min_val is not None:
        df_filtered = df_filtered[df_filtered['Price'] >= min_val]
    if max_val is not None:
        df_filtered = df_filtered[df_filtered['Price'] <= max_val]

    return jsonify(df_filtered.to_dict(orient='records'))



app.run(debug=True)
