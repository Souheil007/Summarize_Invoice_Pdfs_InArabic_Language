from fastapi import FastAPI, Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from utils_to_json import clean_text , extract_text_with_tika , split_into_chunks 
import json ,os
from fastapi.responses import JSONResponse
app = FastAPI()
# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "name": "codingwithroby"})

#In other words, when a client sends a request to this endpoint, they must include a file in the request body, and FastAPI will automatically inject that file into the file parameter of the upload_pdf function.

@app.post("/upload_pdf/")
async def upload_pdf(request: Request, file: UploadFile = File(...)): #In FastAPI, Request is a class that represents an incoming HTTP request
    try:
        pdf_name = file.filename
        save_path = os.path.join("uploaded_files", pdf_name)
        
        # Save the uploaded PDF file
        with open(save_path, "wb") as buffer:
            buffer.write(file.file.read())

        # Extract text from the PDF using Tika
        text_with_tika = extract_text_with_tika(save_path)
        
        # Clean the extracted text
        cleaned_text = clean_text(text_with_tika)
        
        # Split the cleaned text into chunks
        chunks = split_into_chunks(cleaned_text)
        print(chunks)
        # Prepare the response data
        response_data = {
            "file": pdf_name,
            "chunks": chunks
        }
        
        # Read the existing data from the JSON file if it exists
        if os.path.exists('cleaned_data.json'):
            with open('cleaned_data.json', 'r', encoding='utf-8') as infile:
                existing_data = json.load(infile)
        else:
            existing_data = []

        # Append the new data to the existing data
        existing_data.append(response_data)
        
        # Write the updated data back to the JSON file
        with open('cleaned_data.json', 'w', encoding='utf-8') as outfile:
            json.dump(existing_data, outfile, ensure_ascii=False, indent=4)
        
        return JSONResponse(content=response_data)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)