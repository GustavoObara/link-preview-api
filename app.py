from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

# Função para remover "R$", espaços e converter para float
def clean_price(price_text):
    """ Remove qualquer símbolo, mantém apenas números e a vírgula, depois formata o número no padrão brasileiro. """
    # Remove todos os caracteres não numéricos ou vírgula
    numeric_price = re.sub(r'[^\d,]', '', price_text)
    
    # Converte para float usando a vírgula como separador decimal
    float_price = float(numeric_price.replace(',', '.'))
    
    # Formata o número no padrão brasileiro com 2 casas decimais, ponto como separador de milhar e vírgula como decimal
    return "{:,.2f}".format(float_price).replace(",", "v").replace(".", ",").replace("v", ".")

def parse_price(price_text):
    """ Converte o preço formatado como string no estilo brasileiro para float. """
    numeric_price = re.sub(r'[^\d,]', '', price_text)
    return float(numeric_price.replace(',', '.'))

def scrape_page(url):
    headers = {'User-Agent': 'Mozilla/5.0'} 
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Captura do título e imagem do produto
    title = soup.find('meta', property='og:title') or soup.find('title')
    image = soup.find('meta', property='og:image') or soup.find('img', {'id': 'landingImage'})
    
    price = None

    # Scraping para Amazon
    if "amazon" in url:
        try:
            # Captura do preço
            price_whole = soup.find('span', {'class': 'a-price-whole'})
            price_fraction = soup.find('span', {'class': 'a-price-fraction'})
            if price_whole and price_fraction:
                price = clean_price(f"{price_whole.text.strip()}{price_fraction.text.strip()}")
            elif price_whole:  
                price = clean_price(price_whole.text.strip())
            else:
                price = 'No price available'
        except Exception as e:
            print("Something went wrong:", e)
            price = 'Error retrieving price'

    # Scraping para Kabum
    if "kabum" in url:
        try:
            price_pc = None
            # Se o URL contém "monte-seu-pc", busca pelo ID "totals"
            if "monte-seu-pc" in url:
                price_pc = soup.find("h4", id="totals")
            else:
                # Captura do preço final para produtos regulares
                price_element = soup.find("h4", class_="finalPrice")

            # Processamento do preço
            if price_pc:
                # Se 'price_pc' for encontrado, usa ele
                price = clean_price(price_pc.get_text(strip=True))
            elif price_element:
                # Caso contrário, usa o 'finalPrice' (para outros produtos)
                price = clean_price(price_element.get_text(strip=True))
            else:
                # Se nenhum preço for encontrado
                price = 'No price available'
                
        except Exception as e:
            print("Something went wrong:", e)
            price = 'Error retrieving price'

    # Scraping para Steam
    if "steam" in url:
        try:
            # Obtém o preço completo e o preço com desconto
            discount = soup.find("div", class_="discount_final_price")
            price_element = soup.find("div", class_="price")

            fullPrice = None
            discountPrice = None

            if price_element:
                fullPrice = clean_price(price_element.get_text(strip=True))

            if discount:
                discountPrice = clean_price(discount.get_text(strip=True))

            # print(f"Full Price: {fullPrice}, Discount Price: {discountPrice}")

            # Verifica qual preço é menor
            if discountPrice is not None:
                if parse_price(fullPrice) < parse_price(discountPrice):
                    price = fullPrice
                else:
                    price = discountPrice
            else:
                price = fullPrice
            
            # print(f"Final Price: {price}")

            if price is None:
                price = 'Erro ao buscar jogo +18'
                


        except Exception as e:
            print("Something went wrong:", e)
            price = 'Error retrieving price'

    # Captura genérica de preços se nenhum preço específico for encontrado
    if not price:
        try:
            price = 'No generic price available'
        except Exception as e:
            print("Error during generic price search:", e)
            price = 'Error retrieving price'

    # Retorna o objeto JSON com as informações extraídas
    return {
        'image': image['content'] if image and 'content' in image.attrs else image['src'] if image else 'No image available',
        'price': price if price else 'No price available',
        'title': title['content'] if title and 'content' in title.attrs else title.get_text(strip=True) if title else 'No title available',
        'site': url.split('/')[2],
        'url': url
    }

@app.route('/link-preview', methods=['POST'])
def link_preview():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    preview_data = scrape_page(url)
    
    if not preview_data:
        return jsonify({'error': 'Failed to fetch preview data'}), 500
    
    return jsonify(preview_data)

if __name__ == '__main__':
    app.run(debug=True)
