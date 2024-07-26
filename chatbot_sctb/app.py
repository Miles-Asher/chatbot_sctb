from flask import Flask, request, jsonify, render_template
from chatbot import FAQChatbot
from scraper import scrape_website, initialize_pinecone, populate_pinecone
import detectlanguage
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import os

# Load environment data from .env file
load_dotenv()

app = Flask(__name__)

# Configure detectlanguage API key
detectlanguage.configuration.api_key = os.getenv("DETECTLANGUAGE_API_KEY")

# Scrape the website to get FAQs
url = 'https://en.seoulcitybus.com/customer/faq.php'
faqs = scrape_website(url)

# Initialize Pinecone and populate with FAQs
index_name = "faq-index-1"
api_key = os.getenv("PINECONE_API_KEY")
environment = {
    "cloud": os.getenv("PINECONE_ENV_CLOUD"),
    "region": os.getenv("PINECONE_ENV_REGION")
}
index = initialize_pinecone(index_name, api_key, environment)
populate_pinecone(index, faqs)

# Initialize the chatbot with Pinecone index and a similarity threshold
chatbot = FAQChatbot(index_name, api_key)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data['message']
    
    # Detect the language of the question
    input_language = detectlanguage.detect(question)[0]['language']
    if input_language == 'zh':
        input_language = "zh-CN"
    if input_language == 'zh-Hant':
        input_language = "zh-TW"
    
    # Get the answer from the chatbot
    answer = chatbot.get_answer(question)
    
    # Translate the answer back to the detected language if necessary
    if input_language != 'en':
        translator = GoogleTranslator(source='en', target=input_language)
        answer = translator.translate(answer)
    
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=False)
