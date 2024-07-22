from flask import Flask, request, jsonify, render_template
from chatbot import FAQChatbot
from scraper import scrape_website, initialize_pinecone, populate_pinecone

app = Flask(__name__)

# Scrape the website to get FAQs
url = 'https://en.seoulcitybus.com/customer/faq.php'
faqs = scrape_website(url)

# Initialize Pinecone and populate with FAQs
index_name = "faq-index"
api_key = "e382074d-a362-4ae7-aca9-c191d3999ee9"
environment = {
    "cloud": "aws",
    "region": "us-east-1"
}
index = initialize_pinecone(index_name, api_key, environment)
populate_pinecone(index, faqs)

# Initialize the chatbot with Pinecone index
chatbot = FAQChatbot(index_name, api_key, environment)

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
    app.run(debug=False)
