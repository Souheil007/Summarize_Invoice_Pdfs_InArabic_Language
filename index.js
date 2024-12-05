const { GoogleGenerativeAI } = require("@google/generative-ai");
const dotenv = require("dotenv");
const fs = require("fs");
const { createObjectCsvWriter } = require('csv-writer'); // Import csv-writer library
dotenv.config();

// Access your API key as an environment variable
const genAI = new GoogleGenerativeAI(process.env.API_KEY);

async function run() {
    // For text-only input, use the gemini-pro model
    const model = genAI.getGenerativeModel({ model: "gemini-pro" });

    try {
        // Read cleaned_data.json file
        const data = JSON.parse(fs.readFileSync("cleaned_data.json", "utf8"));
        console.log("Cleaned Data:", data);

        const results = [];
        let allText = ""; // Variable to accumulate all response text

        // Iterate over each entry in the JSON data
        for (const entry of data) {
            const fileName = entry.file;
            const chunks = entry.chunks;
            console.log(chunks);

            // Iterate over each chunk in the current entry
            for (const chunk of chunks) {
                const prompt = `سأقدم لك مستنداً يرجى توليد أسئلة وأجوبة بناءً على المحتوى المقدم. قم بتنسيق الاستجابة على النحو التالي: {'أسئلة': ['سؤال 1', 'سؤال 2', ...], 'أجوبة': ['جواب 1', 'جواب 2', ...]}. هنا هو المحتوى: ` + chunk;

                try {
                    const result = await model.generateContent(prompt);
                    const response = await result.response;
                    const text = await response.text();
                    
                    // Log the raw response text
                    console.log("Raw API Response Text:", text);

                    // Append the raw response text to allText
                    allText += `File: ${fileName}\nChunk: ${chunk}\nResponse: ${text}\n\n`;
                    
                    // Add response text to results array
                    const jsonResponse = { file: fileName, chunk, response: text };
                    results.push(jsonResponse);
                } catch (error) {
                    console.error("Error generating content for chunk:", error);
                }
            }
        }

        // Write all response text to a .txt file
        fs.writeFileSync('api_responses.txt', allText, 'utf8');
        console.log("API responses written to api_responses.txt");

        // Convert the .txt file to CSV
        const records = parseTextFileToRecords('api_responses.txt');
        const csvWriter = createObjectCsvWriter({
            path: 'api_responses.csv',
            header: [
                { id: 'file', title: 'File' },
                { id: 'chunk', title: 'Chunk' },
                { id: 'response', title: 'Response' }
            ]
        });

        await csvWriter.writeRecords(records);
        console.log("CSV file created successfully.");

    } catch (error) {
        console.error("Error processing chunks:", error);
    }
}

function parseTextFileToRecords(filePath) {
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const lines = fileContent.split('\n\n'); // Split by double newlines to separate records
    const records = lines.map(line => {
        const [fileLine, chunkLine, responseLine] = line.split('\n');
        if (fileLine && chunkLine && responseLine) {
            return {
                file: fileLine.replace('File: ', ''),
                chunk: chunkLine.replace('Chunk: ', ''),
                response: responseLine.replace('Response: ', '')
            };
        }
    }).filter(record => record); // Remove undefined entries
    return records;
}

run();
