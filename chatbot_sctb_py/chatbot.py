#import csv
import os
import requests
import pandas as pd
import numpy as np
import urllib.request
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, tool
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
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=openai_api_key)


# Load the CSV file
df = pd.read_csv('data/extracted_qna 1.csv')
#print(df.head())
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
df['embeddings'] = df['Question'].apply(lambda x: model.encode(x))
df.to_pickle('questions_embeddings.pkl')

# Function to search for similar questions to query
def find_similar_question(query, df, model, threshold=0.8):
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
def compile_website_content(urls, query, model, threshold=0.6):

    query_embedding = model.encode(query)

    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError if the status code is 4xx or 5xx
            soup = BeautifulSoup(response.content, 'html.parser')
            page_content = soup.get_text(separator="\n", strip=True)

            page_embedding = model.encode(page_content)

            similarity = np.dot(query_embedding, page_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(page_embedding))

            print(similarity)

            if similarity >= threshold:
                return page_content
                        
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred for {url}: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred for {url}: {req_err}")
        except Exception as err:
            print(f"An error occurred for {url}: {err}")
        
    return None

# List of URLs you want to scrape
urls_to_scrape = [
    'https://en.seoulcitybus.com/index.php',
    'https://en.seoulcitybus.com/customer/faq.php',
    'https://en.seoulcitybus.com/service/tour_course_view.php?code=1',
    'https://en.seoulcitybus.com/service/tour_course_view.php?code=2',
    'https://en.seoulcitybus.com/service/tour_course_view.php?code=3',
    'https://en.seoulcitybus.com/service/tour_course_view.php?code=4',
    'https://en.seoulcitybus.com/service/seoulcitytourbus.php',
    'https://en.seoulcitybus.com/service/bus_info.php',
    'https://en.seoulcitybus.com/alliance/alliance_list.php',
    'https://en.seoulcitybus.com/alliance/alliance_use_info.php',
    'https://en.seoulcitybus.com/board/board_view.php?t=N&code=4'
    # Add more URLs as needed
]


# Get available API fields for prompt reference
def get_available_fields():
    """Retrieve and return the available fields from the API."""
    api_url = "https://api.seoulcitybus.com/extend_allience_all_json.php"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            return list(data[0].keys())
    return []

# print(get_available_fields())


# Define the tool functions
@tool
def csv_tool(query: str):
    """Query the CSV file for pre-answered questions"""
    answer = find_similar_question(query, df, model)
    return answer if answer else "No relevant information found in CSV."

@tool
def website_tool(query: str):
    """Query websites for information"""
    compiled_content = compile_website_content(urls_to_scrape, query, model)
    return compiled_content if compiled_content else "No relevant information found on websites."

# @tool
# def business_inquiry_tool(query: str):
#     """Query the API to provide detailed information about a specific business."""
#     with urllib.request.urlopen('https://api.seoulcitybus.com/extend_allience_all_json.php') as url:
#         data = json.load(url)
    
#     query_lower = query.lower()

#     for item in data:
#         if 'name' in item and query_lower in item['name'].lower():
#             info = item.get('info', 'No detailed information available')
#             address = item.get('address', 'Address not provided')
#             hours = item.get('hours', 'Hours not provided')
#             return f"{item['name']} is {info}. It is located at {address} and is open from {hours}. Would you like to know more?"
    
#     return "No relevant information found about the specific business in the API."

@tool
def recommendation_tool(query: str):
    """
    Provide a list of recommendations based on business categories.
    """
    with urllib.request.urlopen('https://api.seoulcitybus.com/extend_allience_all_json.php') as url:
        data = json.load(url)
    
    query_lower = query.lower().rstrip('s')

    recommendations = []
    for item in data:
        for cate_field in ['cate1_name', 'cate2_name']:
            # Get the category field value, which is expected to be a dictionary
            cate_dict = item.get(cate_field, {})
            if isinstance(cate_dict, dict):
                # Check all language variations within the dictionary
                for lang, value in cate_dict.items():
                    if isinstance(value, str) and query_lower in value.lower():
                        recommendations.append(item['name']['en'])
                        break  # No need to check the other languages if a match is found

    if recommendations:
        rec_list = ', '.join(recommendations[:5])  # Limit to 5 recommendations for brevity
        return f"Here are some recommended {query}: {rec_list}. Which one would you like to know more about?"
    
    return "No relevant recommendations found in the API."

    

tools = [csv_tool, website_tool, recommendation_tool]
tool_names = ", ".join([tool.name for tool in tools])
chat_history = []

# Define the prompt template
MEMORY_KEY = "chat_history"
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a knowledgeable assistant focused on providing accurate information about Seoul City Tour Bus services "
            "and other tourist-related inquiries in Seoul. Your task is to respond to user questions by leveraging available tools "
            "efficiently. Follow this order of operations: \n\n"
            "1. **For inquiries about Seoul City Tour Bus services:**\n"
            "   - First, try to find relevant information using the CSV tool.\n"
            "   - If no relevant information is found, use the Website tool to search.\n"
            # "2. **For inquiries about specific businesses in Seoul:**\n"
            # "   - Use the Business Inquiry tool to retrieve detailed information.\n"
            "3. **For recommendations of types of businesses or attractions in Seoul:**\n"
            "   - Use the Recommendation tool to suggest relevant options.\n"
            "4. **General guidelines:**\n"
            "   - Move to the next tool only if the current tool does not yield relevant information.\n"
            "   - Strive to provide the most accurate and concise information available.\n"
            "   - Log all tool usage and fallback scenarios for future reference."
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
    # Prepare the input dictionary with the necessary variables
    input_dict = {
        "input": query,
        "chat_history": chat_history,
        "agent_scratchpad": "",  # Initialize with an empty scratchpad if necessary
    }
    
    # Create the AgentExecutor with the updated input dictionary
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # Invoke the agent with the correct input dictionary
    response = agent_executor.invoke(input_dict)
    
    # Update chat history with the current interaction
    chat_history.extend(
        [
            HumanMessage(content=query),
            AIMessage(content=response["output"]),
        ]
    )

    return response['output']

# *****Example usage*****

# print(chat_history)

# # **CSV tool test**
# query = "Can I bring a wheelchair on the bus?"
# response = handle_query(query)
# print(response)

# # **multilingual CSV tool test**
# query = "버스에 휠체어를 가져갈 수 있나요?"
# response = handle_query(query)
# print(response)

# # **website tool test**
# query = "What bus courses are offered?"
# response = handle_query(query)
# print(response)

# # **multilingual website tool test**
# query = "어떤 버스 코스가 제공되나요?"
# response = handle_query(query)
# print(response)

# # **chat memory test**
# query = "Is the third course currently available?"
# response = handle_query(query)
# print(response)

# # **recommendation tool test**
# query = "Recommend me some good tourist attractions."
# response = handle_query(query)
# print(response)

# # **multilingual recommendation tool test**
# query = "좋은 카페를 추천해 주세요."
# response = handle_query(query)
# print(response)

# print(chat_history)