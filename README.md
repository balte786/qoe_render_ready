
# QoE Report Generator (Render-Ready)

## 🧠 What This Is
FastAPI backend to generate Quality of Earnings (QoE) reports using GPT.

## 🚀 How to Deploy on Render

1. **Create a new GitHub repo** and upload this code
2. **Go to [Render.com](https://render.com)** > New Web Service
3. **Connect your GitHub repo**
4. **Set the start command**:
```
./start.sh
```
5. **Add environment variable**:
```
OPENAI_API_KEY = your-openai-api-key
```

## 🧪 To Test
Once deployed, use the `/upload`, `/generate_qoe`, `/export_docx`, and `/revenue_chart` endpoints via Postman, curl, or a frontend.
