from flask import Flask, request, jsonify, render_template
from chatbot import FAQChatbot
from scraper import scrape_website

app = Flask(__name__)

openai_api_key = "sk-proj-mf80VqVzMcG4X1qfft0mT3BlbkFJHmTjG0veEvUgAcJwBbsn"

# Scrape the website to get FAQs
url = 'https://en.seoulcitybus.com/customer/faq.php'
faqs = scrape_website(url)

# Initialize the chatbot with the scraped FAQs
chatbot = FAQChatbot(faqs, openai_api_key)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data['message']
    answer = chatbot.get_answer(question)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True)