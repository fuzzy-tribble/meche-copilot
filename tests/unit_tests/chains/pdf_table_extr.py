import math
import camelot
import fitz
from meche_copilot.pdf_helpers.get_table_rect import get_table_rect
from tests.visualize import *
from meche_copilot.pdf_helpers.flip_origin_tl_to_bl import *

# get the list of schedule titles and row mark/symbol names
doc = fitz.open('demo-01/engineering_design_drawings.pdf')
p34 = doc[33]
p35 = doc[34]

# PdfPlotter.visualize_blocks(page=p34)
# PdfPlotter.visualize_lines(page=p34)

blocks = p34.get_text_blocks()

# llm tells me schedule titles, number of schedules, row contents headers and remarks
titles = ["ENERGY RECOVERY VENTILATOR SCHEDULE (ALTERNATE)", "ENERGY RECOVERY VENTILATOR SCHEDULE (CONT...)(ALTERNATE)"]
index = ["ERV-1", "ERV-2"]
colulms = ["SYMBOL", "MANUF.", "MODEL", "SERVICE", "TYPE", "LOCATION", "CONFIGURATION", "NOM. SIZE LXWXH (IN.)", "WEIGHT (LBS)", "ENERGY RECOVERY WHEEL - OUTSIDE AIR SIDE - VOLT."] # UNFINISHED
remarks = ""

# get row_blocks
row_blocks =[]
for block in blocks:
    if block[4].startswith('ERV-'):
        row_blocks.append(block[4])

# get row data
erv_row_data = { key: [] for key in index}
for block in row_blocks:
    row_list = block.split('\n')
    if row_list[0] in erv_row_data.keys():
        erv_row_data[row_list[0]].extend(row_list[1:])

rows_df = pd.DataFrame(erv_row_data)
rows_df.shape #58x2
num_row_values = 58

# get the table region (tl and br)
# NOTE: fitz.Rect(x0, y0, x1, y1) where x0,y0 is top left and x1,y1 is bottom right

# get tech rects
title_rect = p34.search_for("ENERGY RECOVERY VENTILATOR SCHEDULE (ALTERNATE)")[0]
last_row_rect = p34.search_for("ERV-2")[1] # the one below the title

table_rect = get_table_rect(page=p34, title_rect=title_rect, last_row_rect=last_row_rect)

marked_page = highlight_rect(page=p34, rect=table_rect)

PdfPlotter.show(page=marked_page, clip=table_rect)

height = p34.bound().bottom_left.y
new_coords = flip_origin_tl_to_bl(table_rect.x0, table_rect.y0, table_rect.x1, table_rect.y1, height)

doc.close()


# TODO - read tables from region table regions or table areas??
# tables = camelot.read_pdf('demo-01/engineering_design_drawings.pdf', pages='34', flavor='stream', edge_tol=500)
# camelot.plot(tables[0], kind='contour').show()

# x1,y1,x2,y2 where (x1,y1) is top left and (x2,y2) is bottom right and the origin of the page is bottom left corner
# TODO - be less stupid
table_areas = list(new_coords)
table_areas = [math.ceil(i) for i in table_areas]
table_areas = f"{table_areas[0]},{table_areas[1]},{table_areas[2]},{table_areas[3]}"
tables = camelot.read_pdf(
    'demo-01/engineering_design_drawings.pdf', 
    pages="34", 
    flavor='lattice', 
    table_areas=[table_areas],
    # line_scale=40, # to detect smaller lines (default 15, greater than 150 and text may be detected as lines)
    # line_scale=80, # better
    line_scale=120,
    # split_text=True,
    # strip_text='\n',
    # columns=['']
    copy_text=['h'], # copy text in spanning cells
    suppress_stdout=False,
    # layout_kwargs={},
    # backend="ghostscript"
    )

assert len(tables) == 1
table_df = tables[0].df

camelot.plot(tables[0], kind='grid').show() # does it get all the lines?
camelot.plot(tables[0], kind='joint').show() # joints?
camelot.plot(tables[0], kind='contour').show()
camelot.plot(tables[0], kind='line').show()

# doesn't seem to be getting the joings and such correct


# can camelot get tables from submittals pretty well or no?

# # assume llm gets the starting page with the mark of the equipment of interest
# doc = fitz.open('demo-01/Subittal_Fans.pdf')
# p3 = doc[3]
# blocks = p3.get_text_blocks()

# tables = camelot.read_pdf('demo-01/Submittal_Fans.pdf', pages="3", flavor='stream') 

import pandas as pd
df = pd.read_pickle('tests/test_data/erv_schedule.pkl')
df = df.T
df = df.iloc[:, 1:] # remove title "column"
# replace empty strings with pd.NA then forward fill
df = df.replace('', pd.NA)
df = df.fillna(method='ffill')

# 