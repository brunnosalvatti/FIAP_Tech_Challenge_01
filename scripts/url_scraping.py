import requests
import csv
from bs4 import BeautifulSoup

base_url = 'https://books.toscrape.com/catalogue/page-{}.html'
book_base_url = 'https://books.toscrape.com/catalogue/'

web_scraping = []
page = 1

while True:
    url = base_url.format(page)
    r = requests.get(url)
    
    if r.status_code != 200:
        break

    print(f'Scraping página {page}...')
    soup = BeautifulSoup(r.text, 'html.parser')
    books = soup.select("article.product_pod")

    for book in books:
        h3_tag = book.find('h3')
        a_tag = h3_tag.find('a')
        book_href = a_tag['href']
        book_url = book_base_url + book_href.replace('../../../', '')

        # Acessa a página do livro individual
        r_book = requests.get(book_url)
        soup_book = BeautifulSoup(r_book.text, 'html.parser')

        # Extrai os dados
        try:
            titulo = soup_book.find('h1').text.strip()
            categoria = soup_book.select('ul.breadcrumb li a')[-1].text.strip()
            preco = soup_book.find('p', class_='price_color').text.strip().replace('£', '')
            estoque = soup_book.find('p', class_='instock availability').text.strip()
            descricao_tag = soup_book.find('div', id='product_description')
            descricao = descricao_tag.find_next_sibling('p').text.strip() if descricao_tag else 'Sem descrição'
            imagem = 'https://books.toscrape.com/' + soup_book.find('img')['src'].replace('../', '')
        except Exception as e:
            print(f"Erro ao processar livro em {book_url}: {e}")
            continue

        # Cria o dicionário com os dados
        livro = {
            'Título': titulo,
            'Categoria': categoria,
            'Preço (£)': preco,
            'Estoque': estoque,
            'Descrição': descricao,
            'Imagem': imagem
        }

        web_scraping.append(livro)

    page += 1  # Próxima página

# Salva os dados em CSV
with open('../data/books_detalhados.csv', 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['Título', 'Categoria', 'Preço (£)', 'Estoque', 'Descrição', 'Imagem']
    writer = csv.DictWriter(f, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(web_scraping)

print("Scraping finalizado com sucesso!")
