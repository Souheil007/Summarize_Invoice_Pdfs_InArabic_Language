import re
from tika import parser
import json
import os

def clean_text(text):
    # Remove non-understandable characters
    #text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Remove bullet points
    text = text.replace('', ' ')
    # Remove multiple spaces and newlines
    #text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def split_into_chunks(text, chunk_size=30):
    # Split the text into chunks of the specified size
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def extract_text_with_tika(PDF_File):
    # Parse the PDF file
    raw = parser.from_file(PDF_File)

    # Extract the content
    return raw['content']

def all_fcts(pdf_dir):
    # Directory containing the PDF files
    pdf_directory = pdf_dir

    # Dictionary to store chunks from all PDF files
    all_chunks = []
    # Iterate through each PDF file in the directory
    for pdf_file in os.listdir(pdf_directory):
        if pdf_file.endswith('.pdf'):
            pdf_path = os.path.join(pdf_directory, pdf_file)
            # Extract text from the PDF using Tika
            text_with_tika = extract_text_with_tika(pdf_path)
            # Clean the extracted text
            cleaned_text = clean_text(text_with_tika)
            # Split the cleaned text into chunks
            chunks = split_into_chunks(cleaned_text)
            # Append chunks to the dictionary with the file name
            #print(chunks)
            all_chunks.append({"file": pdf_file, "chunks": chunks})

    # Save all chunks to a JSON file with UTF-8 encoding
    with open('cleaned_data.json', 'w', encoding='utf-8') as outfile:
        json.dump(all_chunks, outfile, ensure_ascii=False, indent=4)