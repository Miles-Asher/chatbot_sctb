import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    faqs = []
    for faq in soup.select('.faq-item'):
        question = faq.select_one('.question').get_text(strip=True)
        answer = faq.select_one('.answer').get_text(strip=True)
        faqs.append((question, answer))

    return faqs