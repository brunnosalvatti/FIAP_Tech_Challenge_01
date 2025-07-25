import requests
import csv
from bs4 import BeautifulSoup

n = 0
web_scraping = []

# Lê as colunas url (posição 0) e index (posição 1) do CSV
with open('../data/products.csv', 'r', encoding='utf-8') as f:                    # Abertura do Arquivo que Contém as Informações URL e Index
    reader = csv.reader(f)                                                        # 'reader' Recebe o Arquivo
    next(reader)                                                                  # Próxima Linha 
    books = []                                                                    # Criação de Lista que Irá Armazenar a URL
    indices = []                                                                  # Criação de Lista que Irá Armazenar o Index
    for row in reader:                                                            # Para Cada Elemento Dentro de 'reader'
        if row:                                                                   # Se Existir Linha
            books.append(row[0].strip())                                          # Preenchimento de Lista Contendo a URL para Scraping
            indices.append(row[1].strip())                                        # Preenchimento de Lista Contendo o Index

url0 = 'https://books.toscrape.com/'                                              # URL Base

while n < len(books) and requests.get(books[n]).status_code == 200:               # Enquanto n for Menor que a Quantidade de Linhas e o Request for Acessível
    url = books[n]                                                                # URL Recebe o Link da Lista Contendo a URL 
    r = requests.get(url)                                                         # Requisição pela URL
    soup = BeautifulSoup(r.text, 'html.parser')                                   # Soup Receberá o Conteúdo HTML

    # Título e categoria
    breadcrumb = soup.select('ul.breadcrumb li')                                  # Selecionou-se os Elementos Dentro de <ul class=breadcrumb><li></li> Criando Assim uma Lista
    title = breadcrumb[3].text.strip()                                            # Extrai-se o Título
    category = breadcrumb[2].text.strip()                                         # Extrai-se a Categoria

    # Preço
    price = soup.select_one('p.price_color').text.strip()[2:]                    # Seleciona-se o Elemento Dentro de <p class=price_color></p> e se Retira os 2 Primeiros Caracteres

    # Estoque
    stock = soup.select('table.table-striped td')[5].text.strip()                # Seleciona-se o 5º Elemento Dentro de <table class=table-striped><td></td> 
    stock = stock[:-10]                                                          # Retira-se os 10 Últimos Caracteres
    stock = stock[10:]                                                           # Retira-se os 10 Primeiros Caracteres
    stock = int(stock)                                                           # Transforma-se o Valor em um Dado Tipo int

    # Imagem
    img_tag = soup.select_one('#product_gallery img')                           
    img_url = url0 + img_tag['src'][6:] if img_tag else 'not found'

    # Descrição
    desc_div = soup.find('div', id='product_description')
    if desc_div:
        desc_p = desc_div.find_next_sibling('p')
        description = desc_p.text.strip() if desc_p else 'not found'
    else:
        description = 'not found'

    # Rating
    p_tag = soup.find('p', class_='star-rating')
    rating = p_tag['class'][1] if p_tag and len(p_tag['class']) > 1 else 'not found'
    rating = {
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }.get(rating, 0)

    # Pega o index correspondente
    index = indices[n]

    scrap = {
        'Title': title,
        'Category': category,
        'Price': price,
        'Stock': stock,
        'Image': img_url,
        'Rating': rating,
        'Link': url,
        'Description': description,
        'Index': index
    }

    web_scraping.append(scrap)

    print(f"{n}: {title} - {category} - £{price} - Stock: {stock} - Rating: {rating} - Index: {index}")

    n +=1  # Incrementa para a próxima URL

# Salva no CSV final com os nomes corretos
with open('../data/web_scraping.csv', 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['Título', 'Categoria', 'Preço (£)', 'Estoque', 'Imagem', 'Rating', 'Link', 'Descrição', 'Index']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(web_scraping)
