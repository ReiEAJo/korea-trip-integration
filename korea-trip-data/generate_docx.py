from htmldocx import HtmlToDocx
from docx import Document

# Read the HTML content
with open('korea_trip_eda_report.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove the base64 images from HTML because htmldocx might crash on them
# We will just parse the text. NotebookLM cares about text mostly anyway.
import re
# html = re.sub(r'<img[^>]+>', '', html) # Optional: uncomment if htmldocx crashes

new_parser = HtmlToDocx()
doc = Document()
try:
    new_parser.add_html_to_document(html, doc)
    doc.save('korea_trip_eda_report.docx')
    print("Successfully generated DOCX")
except Exception as e:
    print(f"Error: {e}")
