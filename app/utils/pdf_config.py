from playwright.sync_api import sync_playwright
import asyncio


def remove_before_doctype(html_str):
    doctype_index = html_str.find("<!DOCTYPE html>")
    return html_str if doctype_index == -1 else html_str[doctype_index:]


def create_html_file(html_content):
    html_content = remove_before_doctype(html_content)
    with open("my_page.html", "w") as f:
        f.write(html_content)


def html_to_pdf_sync(output_pdf, input_html="my_page.html"):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file:///{input_html}")
        page.pdf(path=output_pdf, format="A4")
        browser.close()
        return output_pdf


async def convert_html_to_pdf(html_content: str, output_file: str):
    create_html_file(html_content)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, html_to_pdf_sync, output_file, "my_page.html"
    )
