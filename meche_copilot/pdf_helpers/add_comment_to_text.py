from operator import is_
import fitz
from loguru import logger

from meche_copilot.pdf_helpers.schemas import PDF_COLORS
from meche_copilot.pdf_helpers.get_page_from_sheet import get_page_from_sheet

def add_comment_to_text(text_to_comment: str, comment_text: str, pdf_fpath=None, doc=None, page=None, sheet=None, outfile=None, stop_after_inst=1):
    """
    Add a comment to a piece of text at page or sheet

    If outfile is none it will overwrite the pdf_fpath
    """

    if (pdf_fpath is not None) and (doc is not None):
        raise ValueError("Only one of pdf_fpath or doc can be specified.")
    
    if (page is not None) and (sheet is not None):
        raise ValueError("Only one of page or sheet can be specified.")
    
    if pdf_fpath is not None:
        doc = fitz.open(pdf_fpath)

    if sheet is not None:
        page_num = get_page_from_sheet(doc=doc, sheet=sheet)
        page = doc[page_num]
    
    pages = [doc[page]] if page is not None else doc

    for i, page in enumerate(pages):
        text_instances = page.search_for(text_to_comment)
        logger.debug(f"text_instances: {text_instances}")
        if len(text_instances) == 0 and i == len(pages) - 1:
            logger.exception(f"Text '{text_to_comment}' not found in page {page}. Exiting")
            break
        for i, inst in enumerate(text_instances):
            logger.debug(f"inst: {inst}")
            annot = page.add_text_annot(
                inst.tl,
                comment_text,
                icon='Comment',
            )
            annot.set_open(is_open=True)
            annot.update()
            if i >= stop_after_inst:
                break

    if outfile is None:
        doc.save(pdf_fpath, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    else:
        doc.save(outfile, encryption=fitz.PDF_ENCRYPT_KEEP)