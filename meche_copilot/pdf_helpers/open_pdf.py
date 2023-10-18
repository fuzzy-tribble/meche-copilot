import platform
import subprocess
from enum import Enum
from loguru import logger

from meche_copilot.pdf_helpers.get_page_from_sheet import get_page_from_sheet

# TODO - incomplete cuz idk how I wanna do this...

class Program(Enum):
    ADOBE = "Adobe Acrobat Reader"
    BLUEBEAM = "Bluebeam"
    BROWSER = "Browser"

def open_pdf(pdf_fpath, program=None, page=None, query=None, sheet=None):
    """
    Open a PDF file with a specific program at page number (eg. 1, 3) xor sheet number (eg. M-802, M-703)
    """

    # either page or sheet can be specified, but not both
    if (page is not None) and (sheet is not None):
        raise ValueError("Only one of page or sheet can be specified.")
    
    page = get_page_from_sheet(pdf_fpath, sheet) if sheet else page

    os_type = platform.system()
    if os_type == "Windows":
        opener = "start -f"  # use start in Windows
    elif os_type == "MacOS":
        opener = "open -a"  # use open in MacOS
    else:
        opener = "xdg-open -f"  # use xdg-open in Linux

    # Open with specified program
    if program == Program.ADOBE:
        opener = "adobe"
    elif program == Program.BLUEBEAM:
        opener = "bluebeam"
    elif program == Program.BROWSER:
        opener = "browser"

    try:
        if page:
            subprocess.call([opener, pdf_fpath + "#page=" + str(page)])
        elif sheet:
            subprocess.call([opener, pdf_fpath + "#nameddest=" + sheet])
        else:
            subprocess.call([opener, pdf_fpath])
    except Exception as e:
        logger.warning(f"Unable to open at specified page or sheet. Opening at page 1. Error: {e}")
        subprocess.call([opener, pdf_fpath])
