Descrição do Projeto:





### É necessário implementar INDEX

Arquitetura do Projeto:






Instruções de Instalação e Configuração:
1) Clonar o repositório 


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