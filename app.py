from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

def clean_price(price_text):
    """ 
    Limpa a string de preço e transforma em um formato bonito para exibição.
    """
    numeric_price = re.sub(r'[^\d,]', '', price_text)  # Remove tudo que não é dígito ou vírgula
    float_price = float(numeric_price.replace(',', '.'))  # Converte pra float
    return "{:,.2f}".format(float_price).replace(",", "v").replace(".", ",").replace("v", ".")  # Formata o preço

def parse_price(price_text):
    """ 
    Transforma a string de preço para float, para realizar comparações. Em casos de produtos
    vendidos com o preço maior do que o produto cadastrado.
    """
    numeric_price = re.sub(r'[^\d,]', '', price_text)  # Remove os lixos
    return float(numeric_price.replace(',', '.'))  # Retorna o preço em float

def scrape_page(url):
    """ 
    Realiza uma busca nos elementos da pagina e retorna um objeto referente a pagina
    do produto oferecido. Com título, preço, imagem, site e a própria url.
    """
    headers = {'User-Agent': 'Mozilla/5.0'} 
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:  #Se não conseguir pegar a página, retorna None
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    title = soup.find('meta', property='og:title') or soup.find('title')  #Tenta pegar o título
    image = soup.find('meta', property='og:image') or soup.find('img', {'id': 'landingImage'})  #Tenta pegar a imagem
    
    price = None # Inicializa a variável de preço

    if "amazon" in url:
        try:
            price_whole = soup.find('span', {'class': 'a-price-whole'})
            price_fraction = soup.find('span', {'class': 'a-price-fraction'})
            if price_whole and price_fraction:
                price = clean_price(f"{price_whole.text.strip()}{price_fraction.text.strip()}")
            elif price_whole:  
                price = clean_price(price_whole.text.strip())
            else:
                price = 'No price available' 
        except Exception as e:
            print("Algo deu errado:", e)
            price = 'Error retrieving price'  

    if "kabum" in url:
        try:
            price_element = soup.find("h4", class_="finalPrice")
            if price_element:
                price = clean_price(price_element.get_text(strip=True))
            else:
                price = 'No price available'                
        except Exception as e:
            print("Algo deu errado:", e)
            price = 'Error retrieving price'

    if "steam" in url:
        try:
            discount = soup.find("div", class_="discount_final_price")
            price_element = soup.find("div", class_="price")

            fullPrice, discountPrice = None, None  

            if price_element:
                fullPrice = clean_price(price_element.get_text(strip=True))  # Pega o preço normal

            if discount:
                discountPrice = clean_price(discount.get_text(strip=True))  # Pega o preço com desconto

            if discountPrice is not None:
                if parse_price(fullPrice) < parse_price(discountPrice):
                    price = fullPrice  # Se o preço normal for menor, fica com ele
                else:
                    price = discountPrice  # Se não, fica com o desconto
            else:
                price = fullPrice  # Se não tem desconto, fica com o normal

            if price is None:
                price = 'Erro ao buscar jogo +18' # Jogos +18 não são abertos na pagina do jogo e sim em um formulário para verificação da idade, vale pesquisar como passar por esse formulário para acessar a pagina do produto

        except Exception as e:
            print("Algo deu errado:", e)
            price = 'Error retrieving price'

    # Se ainda assim não achar um preço, dá um aviso genérico
    if not price:
        try:
            price = 'No generic price available'
        except Exception as e:
            print("Erro durante a busca do preço:", e)
            price = 'Error retrieving price'

    # Retorna tudo que a gente conseguiu pegar
    return {
        'image': image['content'] if image and 'content' in image.attrs else image['src'] if image else 'No image available',
        'price': price if price else 'No price available',
        'title': title['content'] if title and 'content' in title.attrs else title.get_text(strip=True) if title else 'No title available',
        'site': url.split('/')[2],  
        'url': url
    }

@app.route('/link-preview', methods=['POST'])
def link_preview():
    """ 
    Rota que recebe um link e devolve uma prévia dele. 
    Basicamente, é pra facilitar a vida e ter as informações na mão.
    """
    data = request.json
    url = data.get('url')  # Pega a URL do JSON
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400  # Se não passar a URL, não dá pra fazer nada
    
    preview_data = scrape_page(url)  # Faz a chamada pra capturar os dados
    
    if not preview_data:
        return jsonify({'error': 'Failed to fetch preview data'}), 500  # Se não conseguir pegar os dados, avisa

    return jsonify(preview_data)  # Retorna os dados

if __name__ == '__main__':
    app.run(debug=True) 