from html2pdf_chromium import Converter


def remove_before_doctype(html_str):
    doctype_index = html_str.find("<!DOCTYPE html>")
    return html_str if doctype_index == -1 else html_str[doctype_index:]


def create_html_file(html_content, filename="my_page.html"):
    html_content = remove_before_doctype(html_content)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    return filename


def html_to_pdf_sync(input_html="my_page.html", output_pdf="output"):
    converter = Converter()  # create a fresh converter
    pdf_path = f"{output_pdf}.pdf"
    converter.convert_file(input_html, pdf_path)
    return pdf_path


async def convert_html_to_pdf(html_content: str, output_file: str):
    html_file = create_html_file(html_content)
    return html_to_pdf_sync(html_file, output_file)
