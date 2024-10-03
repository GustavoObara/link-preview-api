# Link Preview API

## Descrição

Essa API, construída com Flask, realiza web scraping em websites como Amazon, Kabum e Shopee, retornando dados de pré-visualização de links. A API é útil para obter informações como imagem, preço, título do produto e outras informações diretamente a partir de uma URL.

## Funcionalidade

A API recebe um link via método `POST` e retorna um JSON com os seguintes dados:
- **Imagem** do produto ou página.
- **Preço** do produto, quando disponível.
- **Título** do produto ou página.
- **Site** de origem.
- **URL** original.

## Exemplo de Uso

Faça uma requisição `POST` para o endpoint `/link-preview`, enviando a URL no corpo da requisição:

```bash
POST /link-preview
Content-Type: application/json
{
  "url": "https://www.amazon.com.br/Logitech-MX-Master-3S-Superfície/dp/B0B11LJ69K"
}
```
## Exemplo de Resposta

Se a URL for válida e os dados forem extraídos com sucesso, a resposta será semelhante ao seguinte JSON:

```bash
{
    "image": "https://m.media-amazon.com/images/I/31kOPvuYXLL._SR600%2c315_PIWhiteStrip%2cBottomLeft%2c0%2c35_PIStarRatingFIVE%2cBottomLeft%2c360%2c-6_SR600%2c315_ZA5.719%2c445%2c290%2c400%2c400%2cAmazonEmberBold%2c12%2c4%2c0%2c0%2c5_SCLZZZZZZZ_FMpng_BG255%2c255%2c255.jpg",
    "price": "602,70",
    "title": "Amazon - Mouse sem fio Logitech MX Master 3S com Sensor Darkfield para Uso em Qualquer Superfície, Design Ergonômico, Clique Silencioso, Conexão USB ou Bluetooth - Grafite",
    "site": "Amazon.com.br",
    "url": "https://www.amazon.com.br/Logitech-MX-Master-3S-Superfície/dp/B0B11LJ69K"
}
```

## Tecnologias

- **Flask** para construir a API.
- **BeautifulSoup** para realizar o scraping dos sites.
- **Flask-CORS** para permitir a comunicação entre diferentes domínios.

## Como Rodar o Projeto

1. Clone o repositório:

    ```bash
    git clone https://github.com/GustavoObara/link-preview-api.git
    ```

2. Acesse o diretório do projeto:

    ```bash
    cd link-preview-api
    ```

3. Crie um ambiente virtual (opcional, mas recomendado):

    ```bash
    python -m venv venv
    ```

4. Ative o ambiente virtual:

    - No Windows:

      ```bash
      venv\Scripts\activate
      ```

    - No Linux ou macOS:

      ```bash
      source venv/bin/activate
      ```

5. Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

6. Execute o servidor:

    ```bash
    python app.py
    ```

7. Acesse o endpoint `/link-preview` para realizar as requisições.

    Exemplo de requisição POST:

    ```bash
    curl -X POST http://localhost:5000/link-preview -H "Content-Type: application/json" -d "{\"url\":\"https://www.amazon.com.br/Logitech-MX-Master-3S-Superfície/dp/B0B11LJ69K\"}"
    ```

8. Verifique a resposta no formato JSON com os detalhes do link.