import re
import csv
import os
from tika import parser

def clean_text(text):
    # Remove non-understandable characters
    #text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Remove bullet points
    text = text.replace('', ' ')
    # Remove multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text)
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

# Directory containing the PDF files
pdf_directory = "pdfdocs"

# Open a CSV file for writing
with open('cleaned_data.csv', mode='w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['file', 'chunk']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Write the header
    writer.writeheader()

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
            
            # Write each chunk to the CSV file
            for chunk in chunks:
                writer.writerow({'file': pdf_file, 'chunk': chunk})

print("Data successfully written to cleaned_data.csv")
