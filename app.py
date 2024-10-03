from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

def scrape_page(url):
    headers = {'User-Agent': 'Mozilla/5.0'} 
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    title = soup.find('meta', property='og:title') or soup.find('title')
    image = soup.find('meta', property='og:image') or soup.find('img', {'id': 'landingImage'})
    
    price = None
    if "amazon" in url:
        price_whole = soup.find('span', {'class': 'a-price-whole'})
        price_fraction = soup.find('span', {'class': 'a-price-fraction'})
        if price_whole and price_fraction:
            price = f"{price_whole.text.strip()}{price_fraction.text.strip()}" 
        elif price_whole:  
            price = price_whole.text.strip()
        else:
            price = 'No price available'

    if "kabum" in url:
        try:
            price_element = soup.find("h4", class_="finalPrice")
            if price_element:
                price = price_element.get_text(strip=True)
            else:
                price = 'No price available'
        except Exception as e:
            print("Something went wrong:", e)
            price = 'Error retrieving price'
    
    if "shopee" in url:
        try:
            price_element = soup.find("div", class_="G27FPf")
            if price_element:
                price = price_element.get_text(strip=True)
            else:
                price = 'No price available'
        except Exception as e:
            print("Something went wrong:", e)
            price = 'Error retrieving price'

    if not price:
        try:
            generic_price = soup.find(['span', 'div'], text=lambda t: t and 'price' in t.lower())
            if generic_price:
                price = generic_price.get_text(strip=True)
            else:
                price = 'No price available'
        except Exception as e:
            print("Error during generic price search:", e)
            price = 'Error retrieving price'

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
