import re
import math
import fitz
from loguru import logger
from typing import List

from numpy import mat

def distance_from_corner(match, page_width, page_height):
    ul_distance = math.sqrt(match[0]**2 + match[1]**2)  # Distance from upper-left corner
    lr_distance = math.sqrt((page_width - match[2])**2 + (page_height - match[3])**2)  # Distance from lower-right corner
    ll_distance = math.sqrt(match[0]**2 + (page_height - match[3])**2)  # Distance from lower-left corner
    ur_distance = math.sqrt((page_width - match[2])**2 + match[1]**2)  # Distance from upper-right corner
    return min(ul_distance, lr_distance, ll_distance, ur_distance)

def get_corner_rects(corners: List[str], page_width: float, page_height: float, parts = 4):
    """
    Get the corner of the page.
    """
    corner_rects = []
    for corner in corners:
        if corner == "ul":
            corner_rects.append(fitz.Rect(0, 0, page_width / parts, page_height / parts))
        elif corner == "ur":
            corner_rects.append(fitz.Rect(page_width / parts, 0, page_width, page_height / parts))
        elif corner == "ll":
            corner_rects.append(fitz.Rect(0, page_height / parts, page_width / parts, page_height))
        elif corner == "lr":
            corner_rects.append(fitz.Rect(page_width / parts, page_height / parts, page_width, page_height))
        else:
            raise ValueError("corner must be one of: ul, ur, ll, lr")
    return corner_rects

def get_sheet_from_page(page_num, pdf_fpath=None, doc=None, parts=4, sheet_regex_pattern=r'^[A-Z]{1,2}-\d{3}$', corner=None):
    """
    Get the sheet name from the page number.
    """

    if corner is not None:
        if corner not in ["ul", "ur", "ll", "lr"]:
            raise ValueError("corner must be one of: ul, ur, ll, lr")
        corner_rects = get_corner_rects([corner])

    if (pdf_fpath is not None) and (doc is not None):
        raise ValueError("Only one of pdf_fpath or doc can be specified.")

    if pdf_fpath:
        doc = fitz.open(pdf_fpath)

    page = doc[page_num]

    pattern = re.compile(sheet_regex_pattern)

    # Extract words from the page, find regex matches and get the text and location
    words = page.get_text("words")
    
    # Search for matches using the regular expression pattern
    # ulx: The X-coordinate of the upper-left corner of the bounding box.
    # uly: The Y-coordinate of the upper-left corner of the bounding box.
    # lrx: The X-coordinate of the lower-right corner of the bounding box.
    # lry: The Y-coordinate of the lower-right corner of the bounding box.
    # text: The matched text.
    # size: The font size of the text.
    # flags: Additional flags associated with the text.
    # font: The font index used for the text.
    matches = [w for w in words if pattern.search(w[4])]

    if len(matches) == 0:
        logger.info(f"No matches found on page {page_num}")
        return None
    elif len(matches) == 1:
        logger.info(f"1 Match found on page {page_num} at location {matches[0]}")
        return matches[0]
    else: # matches > 1
        logger.info(f"Multiple matches ({len(matches)}) found on page {page_num} at locations {matches}. Looking for the sheet number in the corners of the page.")

        # Sort the matches by distance from the corners of the page
        sorted_matches = matches.sort(key=lambda match: distance_from_corner(match, page.rect.width, page.rect.height))
        
        # TODO - if corner is specified, only get the matches in that corner

        # Get the sheet number from the match sitting deepest in a corner
        return matches[0]