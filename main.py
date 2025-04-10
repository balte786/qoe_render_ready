from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
import matplotlib.pyplot as plt
import io
import openai
import os
from docx import Document
from docx.shared import Pt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

qoe_cache = {}

def build_prompt(prompt_type: str, data: str) -> str:
    templates = {
        "executive_summary": f"Create an executive summary for a QoE report using this data: {data}",
        "revenue_trends": f"Analyze revenue trends in this monthly income statement: {data}",
        "addbacks": f"Identify one-time or non-recurring expenses for EBITDA adjustments: {data}",
        "working_capital": f"Normalize working capital based on this data: {data}",
    }
    return templates.get(prompt_type, "Invalid prompt type")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    summary = df.describe().to_dict()
    qoe_cache['df'] = df
    qoe_cache['data'] = df.to_dict(orient='records')
    return {"message": "File received", "summary": summary, "data": qoe_cache['data']}

@app.post("/generate_qoe")
async def generate_qoe(payload: dict):
    prompt_type = payload.get("type", "executive_summary")
    data = payload.get("financial_summary", "")
    prompt = build_prompt(prompt_type, data)

    # New code for using the latest API
    response = openai.Completion.create(
        model="gpt-4",  # or "gpt-4-turbo" if you prefer
        prompt=prompt,
        max_tokens=500  # Adjust this as per your needs
    )
    
    content = response['choices'][0]['text'].strip()  # Access the text output

    if 'qoe_report' not in qoe_cache:
        qoe_cache['qoe_report'] = {}

    qoe_cache['qoe_report'][prompt_type] = content

    return {"qoe_summary": content}

@app.get("/export_docx")
async def export_docx():
    doc = Document()
    doc.add_heading("Quality of Earnings Report", 0)
    if 'qoe_report' in qoe_cache:
        for section, text in qoe_cache['qoe_report'].items():
            doc.add_heading(section.replace("_", " ").title(), level=1)
            para = doc.add_paragraph(text)
            para.style.font.size = Pt(11)
    path = "qoe_report.docx"
    doc.save(path)
    return FileResponse(path, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename=path)

@app.get("/revenue_chart")
async def revenue_chart():
    if 'df' not in qoe_cache:
        return {"error": "No data uploaded."}
    df = qoe_cache['df']
    if 'Date' not in df.columns or 'Revenue' not in df.columns:
        return {"error": "Missing 'Date' or 'Revenue' columns."}
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    plt.figure(figsize=(10, 5))
    plt.plot(df['Date'], df['Revenue'], marker='o')
    plt.title('Revenue Trend Over Time')
    plt.xlabel('Date')
    plt.ylabel('Revenue')
    plt.grid(True)
    path = "revenue_chart.png"
    plt.savefig(path)
    plt.close()
    return FileResponse(path, media_type="image/png", filename=path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
