import pandas as pd
import numpy as np
from typing import List
from loguru import logger
from meche_copilot.utils.num_tokens_from_string import num_tokens_from_string

def combine_dataframe_chunks(dfs: List[pd.DataFrame]) -> pd.DataFrame:
    if all(df.shape[1] == dfs[0].shape[1] for df in dfs):
        return pd.concat(dfs, axis=0, ignore_index=True)
    elif all(df.shape[0] == dfs[0].shape[0] for df in dfs):
        return pd.concat(dfs, axis=1)
    else:
        raise ValueError("Chunks do not have consistent shape for concatenation.")

def chunk_dataframe(df: pd.DataFrame, axis=1, num_chunks=None, pct_list=None, max_tokens=None, **kwargs) -> List[pd.DataFrame]:
    """Chunk a dataframe into a list of dataframes using number of chunks xor pct of data in each chunk xor max_tokens in each chunk"""

    if axis not in [0, 1]:
        raise ValueError("axis should be either 0 (rows) or 1 (columns).")

    if sum([num_chunks is not None, pct_list is not None, max_tokens is not None]) != 1:
        raise ValueError(f"Exactly one of num_chunks, pct_list, or max_tokes must be specified. Got {num_chunks}, {pct_list}, {max_tokens}")

    # if using percents, they should not add up to greater than 100
    if pct_list:
        if sum(pct_list) > 100:
            raise ValueError("Sum of pct_list should be 100% or less.")
        num_chunks = len(pct_list) + 1
        pct_list.append(100 - sum(pct_list))
    
    # if using num_chunks (or pct_list), shouldnt be greater than items in axis
    if num_chunks:
      if axis == 0 and num_chunks > df.shape[0]:
          raise ValueError("Number of chunks should not be greater than number of rows.")
      if axis == 1 and num_chunks > df.shape[1]:
          raise ValueError("Number of chunks should not be greater than number of columns.")
    
    chunks = []
    if num_chunks and not pct_list: # split into num_chunks along axis
        logger.debug(f"Splitting df into {num_chunks} chunks along axis {axis}.")
        split_func = np.array_split
        chunks = split_func(df, num_chunks, axis=axis)
    elif pct_list: # split into fractions along axis
        logger.debug(f"Splitting df into {len(pct_list)} chunks along axis {axis} with pct_list {pct_list}.")
        fractions = [pct / 100 for pct in pct_list]
        if axis == 0: # split rows into fractions
            start_idx = 0
            for frac in fractions:
                end_idx = start_idx + int(frac * df.shape[0])
                chunks.append(df.iloc[start_idx:end_idx])
                start_idx = end_idx
        else: # split columns into fractions
            start_idx = 0
            for frac in fractions:
                end_idx = start_idx + int(frac * df.shape[1])
                chunks.append(df.iloc[:, start_idx:end_idx])
                start_idx = end_idx
    else: # split using max_tokens
        logger.debug(f"Splitting df along axis {axis} with max_tokens {max_tokens} per chunk.")
        encoding_name = kwargs.get("encoding_name", "gpt-4")
        start_idx = 0
        prev_tokens = None # To keep track of the previous token size
        while start_idx < df.shape[0] if axis == 0 else start_idx < df.shape[1]:
            for i in range(start_idx, df.shape[0] if axis == 0 else df.shape[1]): # iterate over rows/cols until max_tokens is reached, then append that chunk
                csv_string = df.iloc[start_idx:i+1].to_csv() if axis == 0 else df.iloc[:, start_idx:i+1].to_csv()
                tokens = num_tokens_from_string(csv_string, encoding_name)
                if tokens > max_tokens:
                    # Print the previous token size, not the updated token size
                    logger.debug(f"Adding chunk with shape {df.iloc[start_idx:i].shape if axis == 0 else df.iloc[:, start_idx:i].shape} and prev num tokens {prev_tokens}.")
                    chunks.append(df.iloc[start_idx:i] if axis == 0 else df.iloc[:, start_idx:i])
                    start_idx = i  + 1 # update start_idx
                    break
                prev_tokens = tokens # Save the previous token size
            else: # if loop completes without breaking (i.e., all remaining data fits within max_tokens)
                chunks.append(df.iloc[start_idx:] if axis == 0 else df.iloc[:, start_idx:])
                break
        logger.debug(f"Split df into {len(chunks)} chunks")
    
    return chunks
