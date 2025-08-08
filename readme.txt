Descrição do Projeto:
O projeto tem como objetivo a criação de minha primeira API, sendo uma API documentada e com autenticação JWT.
A API faz o webscraping do site https://books.toscrape.com/ criando um arquivo products.csv que contém o link para cada produto disponível no site.
Após a criação desse arquivo, ele é usado para fazer o webscraping de cada um dos links de products.csv, obtendo assim um arquivo web_scraping.csv contendo informações sobre cada um dos produtos (Título, Categoria, Preço, Imagem, Nota, Link, Descrição,Index).
Esse arquivo gerado é utilizado nas rotas da API para gerar uma análise de dados do site, por meio de diferentes endpoints.



Arquitetura do Projeto:






Instruções de Instalação e Configuração:

1) Clonar o repositório


git clone git@github.com:brunnosalvatti/FIAP_Tech_Challenge_01.git


2) Criar e ativar ambiente virtual venv:

python -m venv venv
venv\Scripts\activate

pip install requirements.txt


3) Web Scraping
O Web Scraping é realizado em 2 etapas. Primeiramente se faz um scrap geral, coletando o link de cada um dos produtos.

scrpits/python url_scraping.py

Após o url_scraping ser feito, ele gerará um arquivo modelo_catalogue.html, onde pode ser analisado o código em html da página para estratégias de scraping. 
Além disso, será gerado um arquivo 'products.csv' que é uma lista de todos os links para todos os livros, ele será usado na segunda fase do books scraping:

scripts/python books_scraping.py

Após o books_scraping ser feito, ele gerará um arquivo modelo_produto.html, onde pode ser analisado o código em html da página para estratégias de scraping.
Além disso, será gerado um arquivo 'books.csv' que contém todas as informações relevantes para cada um dos livros. A partir dele se rodará nossa aplicação em API.



4) Rodando a API
Retorne ao diretório prncipal

python app.py


5) Execute os endpoints









Para acessar rotas sensíveis, use como usuário FIAP e como senha 123456