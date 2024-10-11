from flask import Blueprint, request, jsonify
from app.services.scraper import ScraperService

bp = Blueprint('main', __name__)

# Rota para gerar a pré-visualização de links
@bp.route('/link-preview', methods=['POST'])
def link_preview():
    data = request.json  # Obtém o JSON enviado na requisição
    url = data.get('url')  # Extrai a URL do JSON

    # Valida se a URL foi enviada
    if not url:
        return jsonify({'error': 'URL is required'}), 400 

    scraper = ScraperService(url)  
    preview_data = scraper.scrape() 

    # Valida se a busca foi bem-sucedida
    if not preview_data:
        return jsonify({'error': 'Failed to fetch preview data'}), 500 

    return jsonify(preview_data)  
