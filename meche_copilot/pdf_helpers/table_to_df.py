import camelot
from typing import List
from pathlib import Path
from loguru import logger

def table_to_df(fpath: Path, page_num: str, table_areas: List[str], line_scale: int = 120, copy_text: List[str] = ['h']):
    
    assert len(table_areas) == 1, "only one table area is supported"
    
    tables = camelot.read_pdf(
    str(fpath), 
    pages=page_num, 
    flavor='lattice', 
    table_areas=table_areas,
    # line_scale=40, # to detect smaller lines (default 15, greater than 150 and text may be detected as lines)
    # line_scale=80, # better
    line_scale=line_scale,
    # split_text=True,
    # strip_text='\n',
    # columns=['']
    copy_text=copy_text, # copy text in spanning cells
    suppress_stdout=False,
    # layout_kwargs={},
    # backend="ghostscript"
    )

    assert len(tables) == 1
    table_df = tables[0].df
    logger.debug(f"Extracted table with shape: {table_df.shape}")
    return table_df