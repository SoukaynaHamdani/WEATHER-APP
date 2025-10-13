import pandas as pd
from fastapi.responses import StreamingResponse
import io
from fpdf import FPDF

def export_as_csv(records):
    df = pd.DataFrame(records)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv")

def export_as_json(records):
    return records

def export_as_md(records):
    lines = ["| ID | Query | Location | Date | Temp |\n|----|-------|----------|------|------|"]
    for r in records:
        lines.append(f"| {r['id']} | {r['query']} | {r['location']} | {r['date_queried']} | {r['temperature']} |")
    return "\n".join(lines)

def export_as_pdf(records):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Weather Records", ln=True)
    for r in records:
        pdf.cell(200, 10, txt=f"{r['id']} | {r['query']} | {r['location']} | {r['date_queried']} | {r['temperature']}", ln=True)
    output = io.BytesIO(pdf.output(dest='S').encode('latin-1'))
    output.seek(0)
    return StreamingResponse(output, media_type="application/pdf")
