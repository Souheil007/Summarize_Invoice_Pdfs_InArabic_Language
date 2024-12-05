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
        const data = JSON.parse(fs.readFileSync("cleaned_data_for_summary.json", "utf8"));
        console.log("Cleaned Data:", data);

        const results = [];
        let allText = ""; // Variable to accumulate all response text

        // Iterate over each entry in the JSON data
        for (const entry of data) {
            const fileName = entry.file;
            const text = entry.text; // Use the full text directly
            console.log(text);

            const prompt = `سأقدم لك مستنداً يرجى تلخيص المحتوى المقدم. هنا هو المحتوى: ` + text;

            try {
                const result = await model.generateContent(prompt);
                const response = await result.response;
                const textResponse = await response.text();
                
                // Log the raw response text
                console.log("Raw API Response Text:", textResponse);

                // Append the raw response text to allText
                allText += `File: ${fileName}\nSummary: ${textResponse}\n\n`;
                
                // Add response text to results array
                const jsonResponse = { file: fileName, summary: textResponse };
                results.push(jsonResponse);
            } catch (error) {
                console.error("Error generating summary for file:", error);
            }
        }

        // Write all response text to a .txt file
        fs.writeFileSync('api_summaries.txt', allText, 'utf8');
        console.log("API summaries written to api_summaries.txt");

        // Convert the .txt file to CSV
        const records = parseTextFileToRecords('api_summaries.txt');
        const csvWriter = createObjectCsvWriter({
            path: 'api_summaries.csv',
            header: [
                { id: 'file', title: 'File' },
                { id: 'summary', title: 'Summary' }
            ]
        });

        await csvWriter.writeRecords(records);
        console.log("CSV file created successfully.");

    } catch (error) {
        console.error("Error processing files:", error);
    }
}

function parseTextFileToRecords(filePath) {
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const lines = fileContent.split('\n\n'); // Split by double newlines to separate records
    const records = lines.map(line => {
        const [fileLine, summaryLine] = line.split('\n');
        if (fileLine && summaryLine) {
            return {
                file: fileLine.replace('File: ', ''),
                summary: summaryLine.replace('Summary: ', '')
            };
        }
    }).filter(record => record); // Remove undefined entries
    return records;
}

run();
