import convertapi
import asyncio
from core.config import CONVERT_API_SECRET

def remove_before_doctype(html_str):
    doctype_index = html_str.find("<!DOCTYPE html>")
    return html_str if doctype_index == -1 else html_str[doctype_index:]


def create_html_file(html_content):
    html_content = remove_before_doctype(html_content)
    with open("my_page.html", "w") as f:
        f.write(html_content)


async def convert_html_to_pdf(html_content: str, output_file: str):
    create_html_file(html_content)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, html_to_pdf_sync, output_file, "my_page.html"
    )

def html_to_pdf_sync(output_pdf, input_html="my_page.html"):
    

    # Use your REAL ConvertAPI Secret Key (NOT Secret ID)
    convertapi.api_credentials = CONVERT_API_SECRET

    result = convertapi.convert(
        'pdf',
        {
            'File': input_html,
            'MarginTop': '10',
            'MarginBottom': '10',
            'MarginLeft': '10',
            'MarginRight': '10',
            'PageOrientation': 'Portrait'
        },
        from_format='html'
    )

    result.file.save(output_pdf)
    print(f"PDF saved as {output_pdf}")
    return output_pdf

