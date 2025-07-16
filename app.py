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

    for article in articles[:5]:
        title_tag = article.select_one("h3.title-news a")
        desc_tag = article.select_one("p.description")

        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = title_tag['href']
        summary = desc_tag.get_text(strip=True) if desc_tag else ''
#xu ly anh        
        picture_tag = article.select_one("div.thumb-art picture source")
        image = ''
        if picture_tag:
            data_srcset = picture_tag.get('data-srcset')
            if data_srcset:
                image = data_srcset.split(' ')[0]
        if not image:
            picture_tag = article.select_one(".thumb-art img") or article.select_one("img")
            if picture_tag:
                image = picture_tag.get('data-src') or picture_tag.get('src') or ''
        if image.startswith('//'):
            image = 'https:' + image

        print("Ảnh lấy được:", image)

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
    print(soup.prettify())

    results = []
    articles = soup.select("a.box-category-link-title")

    for article in articles[:5]:
        title = article.get_text(strip=True) 
        link = "https://tuoitre.vn" + article['href']

        if not title:
            continue

        desc_tag = article.find_next('p', class_='box-category-sapo')
        summary = desc_tag.get_text(strip=True) if desc_tag else "Không có mô tả"
#xu ly anh        
        picture_tag = article.select_one(".box-category-link-with-avatar img.box-category-avatar")
        image = ''
        if picture_tag:
            image = picture_tag.get('data-srcset') or picture_tag.get('srcset') or picture_tag.get('data-src') or picture_tag.get('src') or ''
        if image.startswith('//'):
            image = 'https:' + image

        print("Ảnh lấy được:", image)

        results.append({
            'title': title,
            'link': link,
            'source': 'Tuổi Trẻ',
            'image': image,
            'summary': summary
        })

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

        if not title:
            continue

        desc_tag = article.find_next('a', attrs={"class": ["box-category-sapo", "d-block"]})
        summary = desc_tag.get_text(strip=True) if desc_tag else "Không có mô tả"
#xu ly anh
        picture_tag = article.select_one("img.box-category-avatar")
        image = ''
        if picture_tag:
            image = picture_tag.get('data-src') or picture_tag.get('src') or ''
        if image.startswith('//'):
            image = 'https:' + image

        print("Ảnh lấy được:", image)
        results.append({
            'title': title,
            'link': link,
            'source': 'Thanh Niên',
            'image': image,
            'summary': summary
        })
        
    return results
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/results', methods=['GET'])
def results():
    news_results = []
    sources = request.args.getlist('sources')
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')
    full_query = f"{keyword} {location}".strip()
    if 'vnexpress' in sources:
        news_results += scrape_vnexpress(full_query)
    if 'tuoitre' in sources:
        news_results += scrape_tuoitre(full_query)
    if 'thanhnien' in sources:
        news_results += scrape_thanhnien(full_query)
    return render_template('results.html', results=news_results)

if __name__ == '__main__':
    app.run(debug=True)