from fastapi import FastAPI
from fastapi.responses import FileResponse
from src.workflow import workflow_builder
import markdown
import uuid
from pydantic import BaseModel
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from bs4 import BeautifulSoup


class TopicRequest(BaseModel):
    topic: str
    

app = FastAPI()
orchestrator_worker = workflow_builder()


@app.post("/generate")
def generate(req: TopicRequest):
    result = orchestrator_worker.invoke({"topic": req.topic})

    # adjust key based on your state
    report = result.get("final_report", "No report generated")
    return{
        "topic":req.topic,
        "report": report
    }

@app.post("/download")
def download(req: TopicRequest):
    result = orchestrator_worker.invoke({"topic": req.topic})
    report = result.get("final_report", "")
    html = markdown.markdown(report)

    soup = BeautifulSoup(html, "html.parser")

    file_path = f"report_{uuid.uuid4().hex}.pdf"

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(file_path)

    story = []

    # 🔥 Proper parsing
    for element in soup.contents:

        if element.name == "h1":
            story.append(Paragraph(element.text, styles["Heading1"]))

        elif element.name == "h2":
            story.append(Paragraph(element.text, styles["Heading2"]))

        elif element.name == "h3":
            story.append(Paragraph(element.text, styles["Heading3"]))

        elif element.name == "p":
            story.append(Paragraph(element.decode_contents(), styles["Normal"]))

        elif element.name == "ul":
            items = []
            for li in element.find_all("li"):
                items.append(ListItem(Paragraph(li.decode_contents(), styles["Normal"])))
            story.append(ListFlowable(items, bulletType="bullet"))

        story.append(Spacer(1, 12))

    doc.build(story)

    return FileResponse(file_path, filename="report.pdf", media_type="application/pdf")

    