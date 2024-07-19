from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
import uuid

class SessionHistory:
    def __init__(self, messages):
        self.messages = messages

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

        def get_session_history(session_id):
            # Create a session history structure as an object
            return SessionHistory(
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a helpful assistant. Here is some context to help answer the question:\n\n{self.faqs}"
                    }
                ]
            )

        self.history = RunnableWithMessageHistory(
            self.llm,
            get_session_history=get_session_history,
            input_messages_key="input_messages",
            history_messages_key="history",
            output_messages_key="output_messages"
        )

    def get_answer(self, question):
        session_id = str(uuid.uuid4())  # Generate a unique session ID
        input_messages = [
            {
                "role": "user",
                "content": question
            }
        ]
        config = {
            "configurable": {
                "session_id": session_id
            }
        }
        result = self.history.invoke({"input_messages": input_messages}, config=config)
        return result["output_messages"][0]["content"]
