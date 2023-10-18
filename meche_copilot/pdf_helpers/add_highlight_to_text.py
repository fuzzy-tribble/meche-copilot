import fitz
from enum import Enum
from loguru import logger

from meche_copilot.pdf_helpers.schemas import PDF_COLORS
from meche_copilot.pdf_helpers.get_page_from_sheet import get_page_from_sheet

def add_highlight_to_text(text_to_highlight, pdf_fpath=None, doc=None, page=None, sheet=None, highlight_color=PDF_COLORS.gold, outfile=None):
    """
    Find and highlight text in a PDF file.
    If outfile is not specified, the original file will be overwritten.
    If page xor sheet is provided, highlight text on that page only.
    """

    logger.debug(f"highlight_color: {highlight_color}")
    logger.debug(f"highlight_color: {highlight_color.value}")

    # only a page or a sheet can be provided, not both
    if (page is not None and sheet is not None):
        raise ValueError("Only a page or a sheet can be provided, not both.")

    # only pdf_fpath xor doc can be provided, not both
    if (pdf_fpath is not None and doc is not None):
        raise ValueError("Only pdf_fpath xor doc can be provided, not both.")

    if pdf_fpath is not None:
        doc = fitz.open(pdf_fpath)

    if sheet is not None:
        page_num = get_page_from_sheet(doc=doc, sheet=sheet)
        page = doc[page_num]
    
    pages = [doc[page]] if page is not None else doc

    for page in pages:
        text_instances = page.search_for(text_to_highlight)
        for inst in text_instances:
            highlight = page.add_highlight_annot(inst)
            highlight.set_colors({
                "stroke": highlight_color.value, 
                "fill": highlight_color.value
            })

    if outfile is None:
        doc.save(pdf_fpath, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    else:
        doc.save(outfile, encryption=fitz.PDF_ENCRYPT_KEEP)
