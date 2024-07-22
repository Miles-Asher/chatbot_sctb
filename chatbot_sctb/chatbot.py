from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate

class FAQChatbot:
    def __init__(self, faqs, openai_api_key):
        self.faqs = "\n".join([f"Q: {q}\nA: {a}" for q, a in faqs])
        self.llm = OpenAI(api_key=openai_api_key)
        self.prompt = PromptTemplate(
            input_variables=["question", "faqs"],
            template="""
            You are a helpful assistant. Here is some context to help answer the question:

            {faqs}

            Question: {question}
            Answer:
            """
        )

    def get_answer(self, question):
        prompt_text = self.prompt.format(question=question, faqs=self.faqs)
        response = self.llm(prompt_text)
        return response
