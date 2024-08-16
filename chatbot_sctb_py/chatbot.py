#import csv
import os
import requests
import pandas as pd
import numpy as np
import urllib.request
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup
# from langdetect import detect
from sentence_transformers import SentenceTransformer
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, tool
from langchain_openai import ChatOpenAI
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
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
    'https://en.seoulcitybus.com/customer/faq.php',
    'https://en.seoulcitybus.com/index.php',
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
def get_available_fields_with_embeddings():
    api_url = "https://api.seoulcitybus.com/extend_allience_all_json.php"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            fields = list(data[0].keys())
            field_embeddings = {field: model.encode(field) for field in fields}
            return fields, field_embeddings
    return [], {}

# Function to find the closest field match based on similarity
def find_closest_field(query, available_fields, field_embeddings):
    query_embedding = model.encode(query)
    similarities = {field: np.dot(query_embedding, embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(embedding))
                    for field, embedding in field_embeddings.items()}
    closest_field = max(similarities, key=similarities.get)
    return closest_field

# Function to query the API dynamically based on user input
def query_api_for_field(name, field):
    api_url = "https://api.seoulcitybus.com/extend_allience_all_json.php"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        for item in data:
            name_data = item.get("name", {})
            if any(name.lower() in name_value.lower() for name_value in name_data.values()):
                # Search for the field dynamically
                for key, value in item.items():
                    if field.lower() in key.lower():
                        if isinstance(value, dict):
                            # If the value is a dictionary, return the English entry if available
                            return value
                        return value
                return f"Field '{field}' not found for '{name_data.get('en', 'the location')}'."
        return f"'{name}' not found in the data."
    else:
        return "Failed to retrieve data from the API."


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

@tool
def recommendation_tool(query: str):
    """
    Provide a list of recommendations based on business categories.
    When this tool is used, prompt the user to ask for more specific information about anything in the list of recommendations.
    """

    # Load available categories from the API
    with urllib.request.urlopen('https://api.seoulcitybus.com/extend_allience_all_json.php') as url:
        data = json.load(url)

    # Extract unique categories (for both cate1_name and cate2_name fields)
    categories = set()
    for item in data:
        for cate_field in ['cate1_name', 'cate2_name']:
            cate_dict = item.get(cate_field, {})
            if isinstance(cate_dict, dict):
                categories.update(cate_dict.values())

    # Encode the query and categories
    query_embedding = model.encode(query)
    category_embeddings = {category: model.encode(category) for category in categories}

    # Compute similarities
    similarities = {category: np.dot(query_embedding, embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(embedding))
                    for category, embedding in category_embeddings.items()}

    # Find the best matching category
    best_category = max(similarities, key=similarities.get)
    print(f"Best matching category: {best_category}")

    # Use the best matching category for recommendation
    query_lower = best_category.lower().rstrip('s')

    recommendations = []
    for item in data:
        for cate_field in ['cate1_name', 'cate2_name']:
            cate_dict = item.get(cate_field, {})
            if isinstance(cate_dict, dict):
                for lang, value in cate_dict.items():
                    if isinstance(value, str) and query_lower in value.lower():
                        recommendations.append(item['name']['en'])
                        break

    if recommendations:
        rec_list = ', '.join(recommendations[:5])  # Limit to 5 recommendations for brevity
        return rec_list

    return "No relevant recommendations found in the API."

@tool
def business_inquiry_tool(name: str, field_query: str) -> str:
    """Search the Seoul City Bus API and return relevant data based on the business name and desired field."""
    available_fields, field_embeddings = get_available_fields_with_embeddings()

    if("hours" in field_query):
        field_query = "open_time"
    
    mapped_field = find_closest_field(field_query, available_fields, field_embeddings)

    return query_api_for_field(name, mapped_field)

tools = [csv_tool, website_tool, recommendation_tool, business_inquiry_tool]
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
            "   - First, look for similar questions using the CSV tool.\n"
            "   - If no relevant information is found, use the Website tool to search.\n"
            "2. **For inquiries about businesses or attractions other than Seoul City Tour Bus:**\n"
            "   - Use the Business Inquiry tool to retrieve detailed information about affiliate programs, general information, \n"
            "     business hours, closure days, contact info, address and location, or menu.\n"
            "3. **For recommendations of types of businesses or attractions in Seoul:**\n"
            "   - Use the Recommendation tool to suggest relevant options.\n"
            "4. **General guidelines:**\n"
            "   - Always make sure the response is translated into the language of the query.\n"
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
# query = "Can I bring luggage onto the tour bus?"
# response = handle_query(query)
# print(response)

# # **multilingual CSV tool test**
# query = "버스에 휠체어가 탑승할 수 있나요?"
# response = handle_query(query)
# print(response)

# # **website tool test**
# query = "Is Seoul Station close to Gwanghwamun?"
# response = handle_query(query)
# print(response)

# # **multilingual website tool test**
# query = "어떤 버스 코스가 제공되나요?"
# response = handle_query(query)
# print(response)

# # **chat memory test**
# query = "Is course 3 currently available?"
# response = handle_query(query)
# print(response)

# # **recommendation tool test**
# query = "What are some good cafes in Seoul?"
# response = handle_query(query)
# print(response)

# # **multilingual recommendation tool test**
# query = "맛있는 레스토랑을 추천해 주세요."
# response = handle_query(query)
# print(response)

# # **business inquiry tool test**
# query = "when is gyeonbokgung palace open?"
# response = handle_query(query)
# print(response)

# # **business inquiry tool test**
# query = "what days is it closed?"
# response = handle_query(query)
# print(response)

# print("\n\n")
# print(chat_history)