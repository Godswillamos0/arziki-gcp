from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from bs4 import BeautifulSoup
import os

def convert_html_to_pdf(html_content: str, output_filename: str) -> None:
    """
    Converts basic HTML content into a PDF using ReportLab.
    Note: ReportLab cannot render full HTML/CSS like WeasyPrint.
    This function extracts text and writes it into a PDF.
    """

    print(f"\nConverting HTML to PDF: {output_filename}...")

    try:
        # Extract text from HTML
        soup = BeautifulSoup(html_content, "html.parser")
        text_content = soup.get_text(separator="\n")

        # Create PDF
        c = canvas.Canvas(output_filename, pagesize=letter)
        width, height = letter
        y = height - 50  # Start top margin

        # Write line by line
        for line in text_content.split("\n"):
            c.drawString(40, y, line.strip())
            y -= 15  # line spacing
            if y < 50:  # new page
                c.showPage()
                y = height - 50

        c.save()

        print(f"✅ Success: PDF saved to {os.path.abspath(output_filename)}")
        return output_filename

    except Exception as e:
        print(f"❌ PDF conversion failed. Error: {e}")
