import requests
from bs4 import BeautifulSoup
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    faqs = []
    faq_items = soup.select('dt')  # Select all <dt> tags

    for faq in faq_items:
        question_tag = faq.select_one('.stit')
        if question_tag:
            question = question_tag.get_text(strip=True)  # Extract question text
        else:
            #print("Question tag not found")
            continue

        # Find the corresponding answer
        answer_tag = faq.find_next('dd')
        if answer_tag:
            answer_content = answer_tag.select_one('.sdesc')
            if answer_content:
                answer = answer_content.get_text(strip=True)
            else:
                answer = 'No answer provided'
        else:
            answer = 'No answer provided'

        faqs.append((question, answer))
        #print(f"Question: {question}\nAnswer: {answer_tag}\n")

    #print(f"Extracted FAQs: {faqs}")
    return faqs

def initialize_pinecone(index_name, api_key, environment):
    pc = Pinecone(api_key=api_key)
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=384,
            metric='cosine',
            spec=ServerlessSpec(
                cloud=environment['cloud'],
                region=environment['region']
            )
        )
    index = pc.Index(index_name)
    #print(f"Index {index_name} initialized.")
    return index

def populate_pinecone(index, faqs, model_name='all-MiniLM-L6-v2'):
    model = SentenceTransformer(model_name)
    for i, (question, answer) in enumerate(faqs):
        vector = model.encode(question).tolist()
        index.upsert([(f"faq-{i}", vector, {"question": question, "answer": answer})])
        #print(f"FAQ {i} upserted: {question} -> {answer}")

# Example usage for testing
# if __name__ == '__main__':
#     url = 'https://en.seoulcitybus.com/customer/faq.php'
#     faqs = scrape_website(url)
#     index_name = "faq-index"
#     api_key = "e382074d-a362-4ae7-aca9-c191d3999ee9"
#     environment = {
#         "cloud": "aws",
#         "region": "us-east-1"
#     }
#     index = initialize_pinecone(index_name, api_key, environment)
#     populate_pinecone(index, faqs)
