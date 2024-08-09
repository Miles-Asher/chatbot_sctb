#import csv
import os
import requests
import pandas as pd
import numpy as np
import urllib.parse
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_react_agent, AgentExecutor, tool
from langchain_openai import ChatOpenAI
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)


# Load the OpenAI API key from environment variable
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Ensure the API key is set
if not openai_api_key:
    raise ValueError("The OpenAI API key is not set. Please set the 'OPENAI_API_KEY' environment variable.")

# Setup LangChain model with the OpenAI API key
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2, openai_api_key=openai_api_key)

# Load the CSV file
df = pd.read_csv('data/extracted_qna 1.csv')
#print(df.head())
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
df['embeddings'] = df['Question'].apply(lambda x: model.encode(x))
df.to_pickle('questions_embeddings.pkl')

# Function to search for similar questions to query
def find_similar_question(query, df, model, threshold=0.6):
    query_embedding = model.encode(query)

    df['similarity'] = df['embeddings'].apply(lambda x: np.dot(query_embedding, x) / (np.linalg.norm(query_embedding) * np.linalg.norm(x)))

    similar_question = df.loc[df['similarity'].idxmax()]
    print(f"Similarity score: {similar_question['similarity']}")
    print(f"Similar question: {similar_question['Question']}")

    if similar_question['similarity'] >= threshold:
        return similar_question['Answer']
    else:
        return None
    
df = pd.read_pickle('questions_embeddings.pkl')

# Function to load data from URL
def compile_website_content(urls):
    combined_content = ""

    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError if the status code is 4xx or 5xx
            soup = BeautifulSoup(response.content, 'html.parser')
            page_content = soup.get_text(separator="\n", strip=True)
            combined_content += page_content + "\n\n"
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred for {url}: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred for {url}: {req_err}")
        except Exception as err:
            print(f"An error occurred for {url}: {err}")

    return combined_content

# List of URLs you want to scrape
urls_to_scrape = [
    'https://en.seoulcitybus.com/index.php',
    'https://en.seoulcitybus.com/service/tour_course_view.php?code=1',
    'https://en.seoulcitybus.com/service/tour_course_view.php?code=2',
    'https://en.seoulcitybus.com/service/tour_course_view.php?code=3',
    'https://en.seoulcitybus.com/service/tour_course_view.php?code=4',
    'https://en.seoulcitybus.com/service/seoulcitytourbus.php',
    'https://en.seoulcitybus.com/service/bus_info.php',
    'https://en.seoulcitybus.com/alliance/alliance_list.php',
    'https://en.seoulcitybus.com/alliance/alliance_use_info.php',
    'https://en.seoulcitybus.com/customer/faq.php',
    'https://en.seoulcitybus.com/board/board_view.php?t=N&code=4'
    # Add more URLs as needed
]

# Compile all the information into one place

# Define the tool functions
@tool
def csv_tool(query: str):
    """Query the CSV file for pre-answered questions"""
    answer = find_similar_question(query, df, model)
    return answer if answer else "No relevant information found in CSV."

@tool
def website_tool(query: str):
    """Query the a website for information"""
    compiled_content = compile_website_content(urls_to_scrape)
    return compiled_content

@tool
def api_tool(query: str):
    """Query the API for information about other businesses"""
    api_url = "https://api.seoulcitybus.com/extend_allience_all_json.php"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        # Process the API response to find relevant information
        for item in data:
            if query.lower() in item["name"]["en"].lower():
                return item["info"]["en"]
    return "No relevant information found in the API."

tools = [csv_tool, website_tool, api_tool]
tool_names = ", ".join([tool.name for tool in tools])
chat_history = []

# Define the prompt template
MEMORY_KEY = "chat_history"
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant who provides accurate information about Seoul City Tour Bus services. \
            For questions about Seoul City Tour Bus, you should: \
            first try to find information using the CSV tool, \
            second look for relevant information using website tool, \
            finally fall back on a response generated by the LLM. \
            For questions about other aspects of tourism in Korea, you should: \
            first try to find information using the API tool, \
            then fall back on a response generated by the LLM."
        ),
        MessagesPlaceholder(variable_name=MEMORY_KEY),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"), 
    ]
)

llm_with_tools = llm.bind_tools(tools)

# Create the ReAct agent with tools
agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"],
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)

# Function to handle queries
def handle_query(query):
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    response = agent_executor.invoke({"input": query, "chat_history": chat_history})
    chat_history.extend(
        [
            HumanMessage(content=query),
            AIMessage(content=response["output"]),
        ]
    )
        
    if "No relevant information found" in response['output']:
        return "I do not know the answer to this question."
    return response['output']

# Example usage
query = "is there wifi on the bus?"
response = handle_query(query)
print(response)

# query = "what are the operating hours?"
# response = handle_query(query)
# print(response)

# print(chat_history)