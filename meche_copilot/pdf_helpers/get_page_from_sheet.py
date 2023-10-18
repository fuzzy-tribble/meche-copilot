import fitz
from loguru import logger

def get_page_from_sheet(sheet: str, pdf_fpath=None, doc=None):
    """
    Get the page number from the sheet.
    """

    if (pdf_fpath is not None) and (doc is not None):
        raise ValueError("Only one of pdf_fpath or doc can be specified.")

    if pdf_fpath:
        doc = fitz.open(pdf_fpath)

    # check each page
    for i in range(len(doc)-1, -1, -1):  # iterate backwards over all pages
        page = doc[i]
        # define the rectangles representing the corners of the page
        parts = 4
        corners = [
            fitz.Rect(0, 0, page.rect.width / parts, page.rect.height / parts),  # top left
            fitz.Rect(page.rect.width / parts, 0, page.rect.width, page.rect.height / parts),  # top right
            fitz.Rect(0, page.rect.height / parts, page.rect.width / parts, page.rect.height),  # bottom left
            fitz.Rect(page.rect.width / parts, page.rect.height / parts, page.rect.width, page.rect.height)  # bottom right
        ]
        # check each of the four corners of the page for the sheet number
        for corner in corners:
            matches = page.search_for(sheet, hit_max=1, area=corner)
            if matches:  # if the sheet number is found
                logger.info(f"Sheet number {sheet} found on page {i} at location {matches[0]}")
                return i, matches[0]  # return the page number (0-indexed)

    return None  # if the sheet number is not found on any page