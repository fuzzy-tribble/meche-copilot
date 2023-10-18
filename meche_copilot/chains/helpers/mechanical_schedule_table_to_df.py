import math
import fitz
import camelot
import difflib
import pandas as pd
from loguru import logger
from pathlib import Path
from typing import Dict, List
import matplotlib.pyplot as plt

from meche_copilot.pdf_helpers.get_table_rect import get_table_rect
from meche_copilot.pdf_helpers.flip_origin_tl_to_bl import flip_origin_tl_to_bl
from meche_copilot.utils.converters import title_to_filename
from meche_copilot.utils.envars import DATA_CACHE

def preprocess(s):
    # Remove periods, newlines, and make lowercase
    return s.replace('\n', ' ').lower()

def similar(a, b):
    return difflib.SequenceMatcher(None, preprocess(a), preprocess(b)).ratio()


def postprocess_camelot_df(title: str, df: pd.DataFrame, expected_row_data: Dict[str, List[str]], **kwargs) -> pd.DataFrame:

    show_your_work = kwargs.get('show_your_work', False)
    if show_your_work: # write preprocessed df to file
        fname = title_to_filename(title)
        fpath = DATA_CACHE / 'camelot_plots' / f"{fname}_preprocessed_df.csv"
        df.to_csv(fpath, index=False)

    cleaned_df = df.copy() # not necessary?

    keys_list = list(expected_row_data.keys())
    expected_num_rows = len(keys_list) + 1 # +1 for header
    expected_num_cols = len(expected_row_data[keys_list[0]]) + 1
    expected_shape = (expected_num_rows, expected_num_cols)

    logger.debug(f"Postprocessing df with shape: {cleaned_df.shape}. Expected shape: {expected_shape}")

    # DROP FIRST COLUMN IF ITS MALFORMED
    logger.debug(f"Dropping first row if its malformed (ie. contains any of the keys)")
    # NOTE: IDK WHY CAMELOT IS PARSING LIKE THIS BUT THIS BUT THIS IS A WORKAROUND
    if any([key in cleaned_df.iloc[0, 0] for key in keys_list]):
        cleaned_df = cleaned_df.iloc[1:, :] # drop the first row
    logger.debug(f"Expected shape: {expected_shape}, Actual shape: {cleaned_df.shape}")

    # DROP ALL EMPTY ROWS AND COLUMNS
    logger.debug(f"Dropping all empty rows and columns")
    cleaned_df.replace('', pd.NA, inplace=True)
    cleaned_df.dropna(how='all', inplace=True, axis=0) # drop all rows that are all NA
    cleaned_df.dropna(how='all', inplace=True, axis=1) # drop all columns that are all NA
    
    # DROP ALL DUPICATE COLUMNS
    logger.debug(f"Dropping any duplicate columns")
    cleaned_df = cleaned_df.T.drop_duplicates().T # drop duplicate columns
    
    # RESET INDEX AND COLUMNS
    cleaned_df.reset_index(drop=True, inplace=True)
    cleaned_df.columns = range(cleaned_df.shape[1])

    logger.debug(f"At this point, num cols {cleaned_df.shape[1]} should match expected num cols {expected_shape[1]}")
    if show_your_work: # write processed cols to file
        fpath = DATA_CACHE / 'camelot_plots' / f"{fname}_processed_cols.csv"
        cleaned_df.to_csv(fpath, index=False)
    assert cleaned_df.shape[1] == expected_shape[1], f"Expected number of columns {expected_shape[1]} doesn't match actual number of columns {cleaned_df.shape[1]}"
    
    logger.debug(f"Number of columns matches expected number of columns. Working on rows...")

    # GO THROUGH EACH ITEM IN ROW DATA DICT AND IF THAT ROW MATCHES A ROW IN THE DF, ADD THE KEY AS INDEX IF IT DOESN'T ALREADY EXIST
    cleaned_df['UID'] = pd.NA
    threshold = kwargs.get('threshold', 0.9)

    for k, v in expected_row_data.items():
        logger.debug(f"\nChecking key: {k}")
        match_found = False

        for index, row in cleaned_df.iterrows():
            row_list = row.tolist()[:-1]  # exclude uid
            row_list = row_list[1:] # exclude index row

            logger.debug(f"rd row data:", v)
            logger.debug(f"df row data:", row_list)
            

            # Check for same length
            if len(row_list) != len(v):
                logger.debug(f"Row {index} is of different length.")
                continue

            # Check for similarity for each item, but don't include similarity check for NA values
            similarities = [similar(x, y) for x, y in zip(row_list, v) if not (pd.isna(x) or pd.isna(y))]
            logger.debug(f"Similarities for Row {index}:", similarities)

            if all([s > threshold for s in similarities]):
                if pd.isna(cleaned_df.loc[index, 'UID']):
                    cleaned_df.loc[index, 'UID'] = k
                    match_found = True
                    logger.debug(f"Match found for key {k} in Row {index}")
                    break

        if not match_found:
            logger.debug(f"No match found for key: {k}")

    logger.debug(f"Got row matches for {cleaned_df['UID'].count()} rows: {cleaned_df['UID'].tolist()}")

    logger.debug(f"Compressing top rows without a UID into a single row (these should be headers)")

    def custom_agg(s):
        """Custom aggregation function for compressing rows"""
        return ' - '.join([str(x) for x in s if (pd.notna(x) and x != '')])

    # Find the first row with a UID
    first_uid_idx = cleaned_df.index[cleaned_df['UID'].notna()][0]

    # If the first row itself has the UID, then nothing to compress
    if first_uid_idx != 0:

        # Make the first NA row of the UID column "UID"
        cleaned_df.iloc[first_uid_idx, cleaned_df.columns.get_loc('UID')] = 'UID'

        # Generate the compressed row
        subset = cleaned_df.iloc[:first_uid_idx].fillna('')
        compressed_row = subset.agg(custom_agg, axis=0)

        logger.debug(f"Compressed row: {compressed_row}")

        # Drop the original uncompressed rows
        cleaned_df = cleaned_df.drop(index=range(first_uid_idx))

        # Set the columns to the compressed row
        cleaned_df.columns = compressed_row

    logger.debug(f"Done cleaning rows. Checking shape...")
    if show_your_work: # write processed cols to file
        fpath = DATA_CACHE / 'camelot_plots' / f"{fname}_processed_rows.csv"
        cleaned_df.to_csv(fpath, index=False)
    assert cleaned_df.shape[0] == expected_shape[0], f"Expected number of columns {expected_shape[0]} doesn't match actual number of columns {cleaned_df.shape[0]}"
    
    logger.debug(f"Expected shape: {expected_shape}, Actual shape: {cleaned_df.shape}")

    if expected_shape != cleaned_df.shape:
        logger.warning(f"Expected shape: {expected_shape} doesn't match actual shape: {cleaned_df.shape}")
        raise ValueError(f"Expected shape: {expected_shape} doesn't match actual shape: {cleaned_df.shape}")

    return cleaned_df


def mechanical_schedule_table_to_df(pdf_fpath: Path, title: str, last_row: str, page_number: str = None, expected_row_data: Dict[str, List] = None, **kwargs) -> pd.DataFrame:
    """Get the mechanical schedule table data as a dataframe"""

    # NOTE: fitz (and this code) uses 0-indexing for page number
    show_your_work = kwargs.get('show_your_work', False)

    with fitz.open(str(pdf_fpath)) as doc:
        if page_number is None:
            logger.debug(f"Searching for page with title: {title} and last row: {last_row}")
            for i, page in enumerate(doc):
                page_text = page.get_text()
                if title in page_text and last_row in page_text:
                    logger.debug(f"Found page with title: {title} and last row: {last_row} on page: {i+1}")
                    page = doc[i]
                    break
            else:
                raise ValueError(f"Could not find page with title: {title} and last row: {last_row}")
        
        page = doc[int(page_number)]

        # get the enclosing rectange for the table
        table_rect = get_table_rect(page=page, title=title, last_row=last_row, **kwargs)
        height = page.bound().bottom_left.y

        # flip the origin from top left to bottom left for camelot input
        new_coords = flip_origin_tl_to_bl(table_rect.x0, table_rect.y0, table_rect.x1, table_rect.y1, height)

        # x1,y1,x2,y2 where (x1,y1) is top left and (x2,y2) is bottom right and the origin of the page is bottom left corner
        table_areas = list(new_coords)
        table_areas = [math.ceil(i) for i in table_areas]
        table_areas = f"{table_areas[0]},{table_areas[1]},{table_areas[2]},{table_areas[3]}"

        # NOTE: these seem to be the best setting for engineering drawing schedules
        line_scale = kwargs.get('line_scale', 120) # higher line_scale to detect smaller lines (default 15, greater than 150 and text may be detected as lines)
        resolution = kwargs.get('resolution', 500) # higher resolution that camelots default of 300
        copy_text = kwargs.get('copy_text', ['h']) # copy text in spanning cells

        logger.debug(f"Camelot extracting table with line_scale: {line_scale}, resolution: {resolution}, copy_text: {copy_text}")
        tables = camelot.read_pdf(
            str(pdf_fpath), 
            pages=str(page.number+1), # camelot uses 1-indexing for page number
            flavor='lattice', 
            table_areas=[table_areas],
            line_scale=line_scale,
            # split_text=True,
            # strip_text='\n',
            # columns=['']
            copy_text=copy_text,
            suppress_stdout=False,
            # layout_kwargs={},
            # backend="ghostscript"
            resolution=resolution,
            )
        
        logger.debug(f"Camelot found {len(tables)} tables on page: {page.number}")

        if len(tables) != 1:
            raise ValueError(f"Camelot should have found 1 table within selected rectangle on page {page.number} but found {len(tables)}")
        

        logger.debug(f"Parsing report: {tables[0].parsing_report}")

        # if kwarg 'show' is True: save these plots to see what's going on
        show_your_work = kwargs.get('show_your_work', False)
        if show_your_work:
            fname = title_to_filename(title)
            fpath = DATA_CACHE / 'camelot_plots'

            logger.debug(f"Saving camelot table extraction plots to: {fpath}")
            
            fig = camelot.plot(tables[0], kind='grid')
            fig.savefig(fpath / f"{fname}_p{page.number}_grid.png", dpi=resolution)
            plt.close()
            
            fig = camelot.plot(tables[0], kind='joint')
            fig.savefig(fpath / f"{fname}_p{page.number}_joint.png", dpi=resolution)
            plt.close()

            fig = camelot.plot(tables[0], kind='contour')
            fig.savefig(fpath / f"{fname}_p{page.number}_contour.png", dpi=resolution)
            plt.close()

            fig = camelot.plot(tables[0], kind='line')
            fig.savefig(fpath / f"{fname}_p{page.number}_line.png", dpi=resolution)
            plt.close()

        logger.success(f"Creating df from table")
        if expected_row_data is None:
            return tables[0].df
        else:
            postprocessed_df = postprocess_camelot_df(title, tables[0].df, expected_row_data=expected_row_data, **kwargs)
            return postprocessed_df