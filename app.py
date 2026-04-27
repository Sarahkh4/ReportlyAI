from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from src.workflow import workflow_builder
import markdown

app = FastAPI()


# Simple HTML page
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>LLM Report Generator</title>
        </head>
        <body>
            <h1>Generate Report</h1>
            <form action="/generate" method="post">
                <input type="text" name="topic" placeholder="Enter topic" required>
                <button type="submit">Generate</button>
            </form>
        </body>
    </html>
    """


# Endpoint to handle form submission
@app.post("/generate", response_class=HTMLResponse)
def generate(topic: str = Form(...)):
    orchestrator_worker = workflow_builder()
    result = orchestrator_worker.invoke({"topic": topic})

    # adjust key based on your state
    report = result.get("final_report", "No report generated")
    markdown_report = markdown.markdown(report)

    return f"""
    <html>
        <head>
            <title>Report</title>
        </head>
        <body>
            <h1>Generated Report</h1>
            <p>{markdown_report}</p>
            <br>
            <a href="/">Generate another</a>
        </body>
    </html>
    """