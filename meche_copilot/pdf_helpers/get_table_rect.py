import fitz
from typing import List
from loguru import logger

from meche_copilot.pdf_helpers.visualize import outline_rect, highlight_rect, PdfPlotter
from meche_copilot.utils.converters import title_to_filename
from meche_copilot.utils.envars import DATA_CACHE

def choose_closest_rect_below(title_rect: fitz.Rect, last_row_rects: List[fitz.Rect], **kwargs) -> fitz.Rect:
    """Choose the closest rect below the title rect"""
    closest_below_title = last_row_rects[0]
    for last_row_rect in last_row_rects:
        if last_row_rect.y0 > title_rect.y0: # only consider rects below the title
            if last_row_rect.y0 < closest_below_title.y0: # if the current rect is closer to the title than the previous closest in the y direction
                closest_below_title = last_row_rect
            # TODO - should do x direction as well??
    return closest_below_title

def get_table_rect(page: fitz.Page, title: str = None, last_row: str = None, title_rect: fitz.Rect = None, last_row_rect: fitz.Rect = None, include_title=False, x_buffer=10, y_buffer=3, **kwargs):
    """Get the table rect from the page that includes the title and last row"""

    logger.debug(f"Getting table rect for page: {page.number} with title: {title} and last row: {last_row}")

    if (title is None or last_row is None) and (title_rect is None or last_row_rect is None):
        raise ValueError("Must provide either title and last row strings or title and last row rects")

    if title_rect is None:
      title_rect = page.search_for(title)
      if len(title_rect) != 1:
        raise ValueError(f"Found {len(title_rect)} instances of '{title}': {title_rect} on page {page.number}. Schedule titles must be unique.")
      title_rect = title_rect[0]

    # if kwarg 'show' is True: save these plots to see what's going on
    show_your_work = kwargs.get('show_your_work', False)
    if show_your_work:
      t = title_to_filename(title)+'_' if title is not None else ''
      fpath = DATA_CACHE / 'camelot_plots'
      fpath.mkdir(parents=True, exist_ok=True)
      fpath = fpath / f"table_rects_{t}p{page.number}.png"
      marked_page = page

    if last_row_rect is None:
      last_row_rect = page.search_for(last_row)
      if len(last_row_rect) != 1:
        logger.warning(f"Found {len(last_row_rect)} instances of last_row '{last_row}': {last_row_rect} on page {page.number}. Using the one closest to and below the title.")
        selected_last_row_rect = choose_closest_rect_below(title_rect, last_row_rects=last_row_rect)
        logger.debug(f"Using last row rect: {selected_last_row_rect}")
        
        if show_your_work: # save plot of all last row rects outlined and selected highlighted
          logger.debug(f"Saving plot of all last row rects outlined and selected highlighted to: {fpath}")
          for i, rect in enumerate(last_row_rect):
             marked_page = outline_rect(page=marked_page, rect=rect, text=f"last_row_rect_{i}")
          marked_page = highlight_rect(page=marked_page, rect=selected_last_row_rect)
          # PdfPlotter.save(page=marked_page, fpath=str(fpath / "last_row_rects.png"), scale_factor=3.0)
        
        last_row_rect = [selected_last_row_rect]
      last_row_rect = last_row_rect[0]
            
    # get blocks and drawings from page
    drawings = page.get_drawings() # return a list of dicts

    table_top, table_bottom, table_left, table_right = None, None, None, None
    closest_left, closest_right, closest_top, closest_bottom = float('inf'), float('inf'), float('inf'), float('inf')

    # go through each drawing and find the table top boundaries
    for d in drawings:
        if d['type'] == 's':
            items = d['items']
            if items[0][0] == 'l': 
                p1, p2 = items[0][1], items[0][2]
                if type(p1) != fitz.Point or type(p2) != fitz.Point:
                    raise TypeError(f"Expected fitz.Point but got {type(p1)} and {type(p2)} for points p1 and p2 of drawing: {d}")

                # Vertical Line
                if p1.x == p2.x and p1.x < last_row_rect.bottom_left.x and abs(p1.x - last_row_rect.bottom_left.x) < closest_left:
                    if title_rect.bottom_left.y < p1.y < last_row_rect.top_left.y or title_rect.bottom_left.y < p2.y < last_row_rect.top_left.y: # Addressing the TODO about the y-coordinates
                        closest_left = abs(p1.x - title_rect.top_left.x)
                        table_left = p1.x

                # Horizontal Line (Top)
                elif p1.y == p2.y and p1.y < title_rect.top_left.y and abs(p1.y - title_rect.top_left.y) < closest_top:
                    closest_top = abs(p1.y - title_rect.top_left.y)
                    table_top = p1.y
                    table_right = max(p1.x, p2.x)

                # Horizontal Line (Bottom)
                elif p1.y == p2.y and p1.y > last_row_rect.bottom_right.y and abs(p1.y - last_row_rect.bottom_right.y) < closest_bottom:
                    closest_bottom = abs(p1.y - last_row_rect.bottom_right.y)
                    table_bottom = p1.y
                    table_right = max(p1.x, p2.x)

    logger.debug(f"table_top={table_top}, table_bottom={table_bottom}, table_left={table_left}, table_right={table_right}")

    table_rect = fitz.Rect(table_left, table_top, table_right, table_bottom)

    if not include_title:
      table_rect.y0 = title_rect.y1

    if x_buffer > 0:
      table_rect.x0 -= x_buffer
      table_rect.x1 += x_buffer
    
    if y_buffer > 0:
      table_rect.y0 -= y_buffer
      table_rect.y1 += y_buffer

    if show_your_work:
      logger.debug(f"Saving plot of table rect to: {fpath}")
      marked_page = outline_rect(page=marked_page, rect=table_rect, text="table_rect", color=(0, 0, 1))
      PdfPlotter.save(page=marked_page, fpath=str(fpath), scale_factor=3.0)

    return table_rect