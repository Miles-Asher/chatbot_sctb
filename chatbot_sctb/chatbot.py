import openai
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import detectlanguage
from deep_translator import GoogleTranslator

class FAQChatbot:
    def __init__(self, index_name, api_key, environment, model_name='paraphrase-multilingual-MiniLM-L12-v2', similarity_threshold=0.6):
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold
        openai.api_key = 'sk-proj-l8zErLVsj7miqVX1TTEYT3BlbkFJ1RIOv6CHJcFsJ6pKGwfa'
        self.client = openai.OpenAI(api_key=openai.api_key)

    def get_answer(self, question):
        vector = self.model.encode(question).tolist()
        response = self.index.query(vector=vector, top_k=1, include_metadata=True)
        
        if response['matches']:
            top_match = response['matches'][0]
            score = top_match['score']
            answer = top_match['metadata']['answer']
            
            # Check if the score meets the similarity threshold
            #print(score)
            if score >= self.similarity_threshold:
                return answer
        
        # Fall back to GPT model if no suitable match is found
        return self.get_gpt_answer(question)

    def get_gpt_answer(self, question):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()

    def translate_text(self, text, target_language):
        translator = GoogleTranslator(source='auto', target=target_language)
        return translator.translate(text)
