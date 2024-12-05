from fastapi import FastAPI, Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
from utils_to_json import clean_text, extract_text_with_tika, split_into_chunks
import json, os

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Initialize vLLM
llm = LLM(model="./t5_base", adapter_path="./t5_model")
tokenizer = AutoTokenizer.from_pretrained("./t5_base")

samplee = "اشرف رئيس الجمهوريه الباجي قايد السبسي اليوم بقصر قرطاج موكب منح الوسام الوطني للاستحقاق الثقافي الفنانين والمبدعين بمناسبه انعقاد ايام قرطاج السينمائيه والفنانون الصنف عبد الرحمان سيساكو موريتانيا جميل راتب مصر ميشال خليفي فلسطين ادريسا ودراغو بوركينا فاسو محمد ملص سوريا رضا الباهي تونس الحضور عمر الخليفي تونس الصنف الثاني عبد العزيز بن ملوكه تونس نجيب تونس منصف شرف الدين تونس الحضور الصنف الثالث ابراهيم تونس الخياطي تونس الحضور تونس عليها الحضور شوقي الماجري تونس الصنف الرابع كوثر بن تونس"

def generate_summary(input_text, llm):
    input_prompt = f"""
      Summarize the following conversation.
      {input_text}
      Summary:
    """
    # Define sampling parameters for the generation
    sampling_params = SamplingParams(temperature=0.7, max_new_tokens=500)

    # Generate the summary using vLLM
    outputs = llm.generate(input_prompt, sampling_params=sampling_params)

    # Extract the generated summary text
    output_text = outputs[0].text.strip()
    return output_text

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "name": "codingwithroby"})

@app.post("/upload_pdf/")
async def upload_pdf(request: Request, file: UploadFile = File(...)):
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
        
        output = generate_summary(samplee, llm=llm)
        
        # Summarize each chunk using the fine-tuned model
        summaries = []
        for chunk in chunks:
            summaries.append(generate_summary(chunk, llm=llm))

        # Prepare the response data
        response_data = {
            "file": pdf_name,
            "chunks": chunks,
            "summaries": summaries,
            "sample": samplee,
            "generated_summary": output,
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
