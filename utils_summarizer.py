import re
from tika import parser
import json
import os

def clean_text(text):
    # Remove non-understandable characters
    # text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Remove bullet points
    text = text.replace('', ' ')
    # Remove multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def extract_text_with_tika(PDF_File):
    # Parse the PDF file
    raw = parser.from_file(PDF_File)

    # Extract the content
    return raw['content']

# Directory containing the PDF files
pdf_directory = "pdfdocs"

# List to store data from all PDF files
all_data = []
# Iterate through each PDF file in the directory
for pdf_file in os.listdir(pdf_directory):
    if pdf_file.endswith('.pdf'):
        pdf_path = os.path.join(pdf_directory, pdf_file)
        # Extract text from the PDF using Tika
        text_with_tika = extract_text_with_tika(pdf_path)
        # Clean the extracted text
        cleaned_text = clean_text(text_with_tika)
        # Append the cleaned text to the list with the file name
        all_data.append({"file": pdf_file, "text": cleaned_text})

# Save all data to a JSON file with UTF-8 encoding
with open('cleaned_data_for_summary.json', 'w', encoding='utf-8') as outfile:
    json.dump(all_data, outfile, ensure_ascii=False, indent=4)
