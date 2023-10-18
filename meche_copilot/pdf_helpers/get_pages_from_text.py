import fitz
from loguru import logger
from typing import List


def get_pages_from_text(text, pdf_fpath=None, doc=None) -> List[str]:
    """
    Given a text string, return the page number(s) where it is found in the pdf.
    """
    logger.info(f"Searching for '{text}' in pdf")
    found_on_pages = []

    # only pdf_fpath xor doc can be provided, not both
    if (pdf_fpath is not None and doc is not None):
        raise ValueError("Only pdf_fpath xor doc can be provided, not both.")

    if pdf_fpath is not None:
        logger.debug(f"Opening pdf: {pdf_fpath}")
        doc = fitz.open(pdf_fpath)

    for i, page in enumerate(doc):
        text_instances = page.search_for(text)
        if len(text_instances) > 0:
            found_on_pages.append(i)
    
    logger.debug(f"Found {text} on pages: {found_on_pages}")
    return found_on_pages