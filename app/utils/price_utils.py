import re

# Função para limpar a string de preço e formatar para um formato legível
def clean_price(price_text):
    """ Limpa a string de preço e transforma em um formato bonito para exibição. """
    numeric_price = re.sub(r'[^\d,]', '', price_text)
    float_price = float(numeric_price.replace(',', '.'))
    return "{:,.2f}".format(float_price).replace(",", "v").replace(".", ",").replace("v", ".")

# Função para transformar a string de preço em um valor float
def parse_price(price_text):
    """ Transforma a string de preço para float. """
    numeric_price = re.sub(r'[^\d,]', '', price_text) 
    return float(numeric_price.replace(',', '.'))  
