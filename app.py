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
    articles = soup.select("h3.title-news a")
    for article in articles[:10]:
        title = article.get_text(strip=True)
        link = article['href']  
        print (title, link)
        results.append({'title': title, 'link': link, 'source': 'VNEXPRESS'})

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


@app.route('/', methods=['GET', 'POST'])
def index():
    news_results = []
    if request.method == 'POST':
        keyword = request.form['keyword']
        location = request.form.get('location', '')
        full_query = f"{keyword} {location}".strip()
        news_results = (
                        scrape_vnexpress(full_query) +
                        scrape_tuoitre(full_query) +
                        scrape_thanhnien(full_query)
        )

    return render_template('index.html', results=news_results)

if __name__ == '__main__':
    app.run(debug=True)