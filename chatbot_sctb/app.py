from flask import Flask, request, jsonify, render_template
from chatbot import FAQChatbot
from scraper import scrape_website, initialize_pinecone, populate_pinecone
import detectlanguage
from deep_translator import GoogleTranslator

app = Flask(__name__)

# Configure detectlanguage API key
detectlanguage.configuration.api_key = "908a865c318ba9be28bea2e795a74096" # Move to .env

# Scrape the website to get FAQs
url = 'https://en.seoulcitybus.com/customer/faq.php'
faqs = scrape_website(url)

# Initialize Pinecone and populate with FAQs
index_name = "faq-index-1"
api_key = "e382074d-a362-4ae7-aca9-c191d3999ee9" # Move to .env
environment = {
    "cloud": "aws",
    "region": "us-east-1"
}
index = initialize_pinecone(index_name, api_key, environment)
populate_pinecone(index, faqs)

# Initialize the chatbot with Pinecone index and a similarity threshold
similarity_threshold = 0.6  # Adjust this threshold as needed
chatbot = FAQChatbot(index_name, api_key, environment, similarity_threshold=similarity_threshold)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data['message']
    
    # Detect the language of the question
    input_language = detectlanguage.detect(question)[0]['language']
    #print(input_language)
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
