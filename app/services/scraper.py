import requests
from bs4 import BeautifulSoup
from app.utils.price_utils import clean_price, parse_price

# Classe para realizar o scraping de páginas e extrair informações
class ScraperService:
    def __init__(self, url):
        self.url = url 
        self.soup = self.fetch_page()  

    # Método para buscar o conteúdo da página com cabeçalhos
    def fetch_page(self):
        headers = {'User-Agent': 'Mozilla/5.0'}  
        response = requests.get(self.url, headers=headers)  
        if response.status_code == 200:  
            return BeautifulSoup(response.content, 'html.parser')  
        return None  # Retorna None se a página não puder ser carregada

    # Método para obter o preço da página
    def get_price(self):
        price = None
        if "amazon" in self.url:
            price = self._scrape_amazon_price()  
        elif "kabum" in self.url:
            price = self._scrape_kabum_price()  
        elif "steam" in self.url:
            price = self._scrape_steam_price()  
        return price

    # Método privado para busca de preços na Amazon
    def _scrape_amazon_price(self):
        try:
            price_whole = self.soup.find('span', {'class': 'a-price-whole'}) 
            price_fraction = self.soup.find('span', {'class': 'a-price-fraction'})  
            if price_whole and price_fraction:
                return clean_price(f"{price_whole.text.strip()}{price_fraction.text.strip()}")  # Formata o preço
            elif price_whole:
                return clean_price(price_whole.text.strip())  # Retorna parte inteira se parte fracionada estiver ausente
        except Exception as e:
            print("Erro Amazon:", e)  
        return 'No price available' 

    # Método privado para busca de preços na Kabum
    def _scrape_kabum_price(self):
        try:
            price_element = self.soup.find("h4", class_="finalPrice")
            return clean_price(price_element.get_text(strip=True)) if price_element else 'No price available'
        except Exception as e:
            print("Erro Kabum:", e)
        return 'No price available'

    # Método privado para busca de preços na Steam
    def _scrape_steam_price(self):
        """
        A Steam possui algumas páginas com conteúdo restrito para maiores de 18 anos, que exigem a submissão de um formulário de confirmação de idade antes de serem acessadas.
        Além disso, a plataforma contém seções de recomendações, onde é necessário verificar a viabilidade de não obter o preço dos itens recomendados.
        Fica para uma próxima alteração ou melhoria futura, pois o atual foco é garantir a extração de preços dos itens principais, evitando complicações em páginas com bloqueios ou conteúdo dinâmico. 
        Sinta-se à vontade para contribuir caso tenha uma solução para esses cenários.
        """
        try:
            discount = self.soup.find("div", class_="discount_final_price")  # Encontra preço com desconto
            price_element = self.soup.find("div", class_="price")  # Encontra o preço original
            fullPrice = clean_price(price_element.get_text(strip=True)) if price_element else None  # Formata preço original
            discountPrice = clean_price(discount.get_text(strip=True)) if discount else None  # Formata preço com desconto
            return discountPrice if discountPrice and parse_price(fullPrice) > parse_price(discountPrice) else fullPrice  # Retorna o menor preço
        except Exception as e:
            print("Erro Steam:", e) 
        return 'No price available' 

    # Método para realizar a busca de informações da página
    def scrape(self):
        title = self.soup.find('meta', property='og:title') or self.soup.find('title')  
        image = self.soup.find('meta', property='og:image') or self.soup.find('img', {'id': 'landingImage'})  
        price = self.get_price()  

        # Retorna as informações
        return {
            'image': image['content'] if image and 'content' in image.attrs else 'No image available',  
            'price': price,  
            'title': title['content'] if title and 'content' in title.attrs else 'No title available',  
            'site': self.url.split('/')[2],  
            'url': self.url  
        }
