import fitz  # PyMuPDF
import requests

def parse_plan_data(pdf_url):
    """
    A function to parse PDF from a URL into structured text with page markers.

    Args:
        pdf_url (str): URL to the PDF file.

    Returns:
        str: Parsed data as a string.
    """
    # Request the PDF file from the URL
    response = requests.get(pdf_url)
    response.raise_for_status()

    # Load the PDF file
    document = fitz.open(stream=response.content, filetype="pdf")

    parsed_text = []
    for page_num, page in enumerate(document, start=1):
        # Add page number marker
        parsed_text.append(f'Page {page_num}\n{"="*40}\n')
        # Extract text from the page
        parsed_text.append(page.get_text('text'))

    return '\n'.join(parsed_text)