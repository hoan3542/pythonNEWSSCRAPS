from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_vnexpress(query):
    url = f"https://timkiem.vnexpress.net?q={query.replace(' ', '+')}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup.prettify())
    results = []
    articles = soup.select("article.item-news")
    for article in articles[:10]:
        title_tag = article.select_one("h3.title-news a")
        img_tag = article.select_one("img.thumb") or article.select_one("img.thumb-art") or article.select_one("img")
        desc_tag = article.select_one("p.description")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = title_tag['href']
        image = ''
        if img_tag:
            image = img_tag.get('data-src') or img_tag.get('src') or ''
            if image.startswith('//'):
                image = 'https:' + image
        summary = desc_tag.get_text(strip=True) if desc_tag else ''

        results.append({
            'title': title,
            'link': link,
            'source': 'VNEXPRESS',
            'image': image,
            'summary': summary
        })

    return results
def scrape_tuoitre(query):
    url = f"https://tuoitre.vn/tim-kiem.htm?keywords={query.replace(' ', '+')}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    articles = soup.select("a.box-category-link-title")
    for article in articles[:5]:
        title = article.get_text(strip=True)
        link = "https://tuoitre.vn" + article['href']
        results.append({'title': title, 'link': link, 'source': 'Tuổi Trẻ'})
    return results

def scrape_thanhnien(query):
    url = f"https://thanhnien.vn/tim-kiem/{query.replace(' ', '%20')}.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    articles = soup.select("a.box-category-link-title")

    for article in articles[:5]:
        title = article.get_text(strip=True)
        link = article['href']
        if not link.startswith("http"):
            link = "https://thanhnien.vn" + article['href']
        results.append({'title': title, 'link': link, 'source': 'Thanh Niên'})
    return results
def scrape_tienphong(query):
    url = f"https://tienphong.vn/tim-kiem/{query.replace(' ', '%20')}.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    articles = soup.select("h2.story__heading a.cms-link")

    for article in articles[:5]:
        title = article.get_text(strip=True)
        link = article['href']
        if not link.startswith("http"):
            link = "https://tienphong.vn/" + article['href']
        results.append({'title': title, 'link': link, 'source': 'Tiền Phong'})
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    news_results = []
    sources = []
    if request.method == 'POST':
        keyword = request.form['keyword']
        location = request.form.get('location', '')
        full_query = f"{keyword} {location}".strip()
        sources = request.form.getlist('sources')
    if 'vnexpress' in sources:
        news_results += scrape_vnexpress(full_query)
    if 'tuoitre' in sources:
        news_results += scrape_tuoitre(full_query)
    if 'thanhnien' in sources:
        news_results += scrape_thanhnien(full_query)
    if 'tienphong' in sources:
        news_results += scrape_tienphong(full_query)

    return render_template('index.html', results=news_results)

if __name__ == '__main__':
    app.run(debug=True)