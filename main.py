from fastapi import FastAPI, Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from transformers import T5Tokenizer, T5ForConditionalGeneration
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel
from utils_to_json import clean_text, extract_text_with_tika, split_into_chunks
import json, os

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")
# Set paths
adapter_path = "./t5_model_r512_alpha1024"  # Path to the PEFT adapter
base_model_id = "./t5_base"  # Base model ID for T5

# Load the base model
base_model = AutoModelForSeq2SeqLM.from_pretrained(base_model_id)

# Load the PEFT adapter
model = PeftModel.from_pretrained(base_model, adapter_path)

# Load the tokenizer
tokenizer = AutoTokenizer.from_pretrained("./t5_base")

# Set the model to use cache for inference (for efficiency)
model.config.use_cache = True
samplee="اشرف رئيس الجمهوريه الباجي قايد السبسي اليوم بقصر قرطاج موكب منح الوسام الوطني للاستحقاق الثقافي الفنانين والمبدعين بمناسبه انعقاد ايام قرطاج السينمائيه والفنانون الصنف عبد الرحمان سيساكو موريتانيا جميل راتب مصر ميشال خليفي فلسطين ادريسا ودراغو بوركينا فاسو محمد ملص سوريا رضا الباهي تونس الحضور عمر الخليفي تونس الصنف الثاني عبد العزيز بن ملوكه تونس نجيب تونس منصف شرف الدين تونس الحضور الصنف الثالث ابراهيم تونس الخياطي تونس الحضور تونس عليها الحضور شوقي الماجري تونس الصنف الرابع كوثر بن تونس"
def generate_summary(input_text, llm):
    input_prompt = f"""
      Summarize the following conversation.
      {input_text}
      Summary:
    """
    inputs = tokenizer(input_prompt, return_tensors='pt', padding=True, truncation=True, max_length=512)

    # Move tensors to the same device as the model
    input_ids = inputs['input_ids'].to(llm.device)
    attention_mask = inputs['attention_mask'].to(llm.device)

    tokenized_output = llm.generate(
        input_ids,
        attention_mask=attention_mask,
        min_length=30,
        max_length=500,  # Adjusted max_length
        pad_token_id=tokenizer.eos_token_id  #end-of-sequence (EOS)
    )

    output = tokenizer.decode(tokenized_output[0], skip_special_tokens=True)
    return output

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
        
        output = generate_summary(samplee, llm=model)
        
        # Summarize each chunk using the fine-tuned model
        summaries = []
        for chunk in chunks:
            #inputs = tokenizer.encode("summarize: " + chunk, return_tensors="pt", max_length=512, truncation=True)
            #summary_ids = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
            #summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            summaries.append(generate_summary(chunk, llm=model))

        # Prepare the response data
        response_data = {
            "file": pdf_name,
            "chunks" : chunks,
            "summaries": summaries,
            "sample":samplee ,
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
