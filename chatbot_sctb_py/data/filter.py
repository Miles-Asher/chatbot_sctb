import pandas as pd
import json
import re

# Use raw string literals for file paths
csv_file_path = r'C:\xampp\htdocs\chatbot\chatbot_sctb_py\data\Inquiry data as of July 2023.csv'
json_file_path = r'C:\xampp\htdocs\chatbot\chatbot_sctb_py\data\qna_20240729182755.txt'

# Load the CSV file
csv_data = pd.read_csv(csv_file_path)
csv_codes = csv_data['code'].astype(str).tolist()

# Load the JSON data
with open(json_file_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# Filter dictionaries from the JSON data where the "code" key matches the values in csv_codes
filtered_json_data = [entry for entry in json_data if str(entry['code']) in csv_codes]

# Define a function to extract the relevant question part
def extract_question(memo):
    # Patterns for different languages
    patterns = [
        r'Inquiry : (.+)',             # English
        r'문의내용 : (.+)',               # Korean
        r'お問い合わせ内容：(.+)',       # Japanese
        r'询价内容：(.+)',               # Chinese
    ]
    for pattern in patterns:
        match = re.search(pattern, memo, re.DOTALL)
        if match:
            return match.group(1).strip()
    return memo.strip()

# Extract only the filtered question and answer texts
extracted_data = [{'question': extract_question(entry['memo']), 'answer': entry['re_memo']} for entry in filtered_json_data]

# Convert to DataFrame for easier manipulation and saving
extracted_df = pd.DataFrame(extracted_data)

# Save the extracted data to a new CSV file
extracted_df.to_csv(r'C:\xampp\htdocs\chatbot\chatbot_sctb_py\data\extracted_qna.csv', index=False, encoding='utf-8')

print("Extraction complete. The data has been saved to 'extracted_qna.csv'.")
