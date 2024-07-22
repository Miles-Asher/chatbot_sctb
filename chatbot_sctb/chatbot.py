from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

class FAQChatbot:
    def __init__(self, index_name, api_key, environment, model_name='all-MiniLM-L6-v2'):
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)
        self.model = SentenceTransformer(model_name)

    def get_answer(self, question):
        vector = self.model.encode(question).tolist()
        #print(f"Query vector: {vector}")
        response = self.index.query(vector=vector, top_k=1, include_metadata=True)
        #print(f"Response from Pinecone: {response}")
        
        if response['matches']:
            answer = response['matches'][0]['metadata']['answer']
        else:
            answer = "Sorry, I couldn't find an answer to your question."
        
        return answer
