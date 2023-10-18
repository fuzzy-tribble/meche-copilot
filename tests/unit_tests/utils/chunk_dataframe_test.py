"""
Test chunk dataframe
"""
import pytest
from meche_copilot.pdf_helpers.add_highlight_to_text import add_highlight_to_text

@pytest.mark.skip(reason="Scaffold needs convert to pytest")
def test_chunk_dataframe():
    pass

# SCAFFOLD
# import pandas as pd
# from typing import List

# from meche_copilot.schemas import *
# from meche_copilot.utils.config import find_config
# from meche_copilot.utils.chunk_dataframe import chunk_dataframe

# config = SessionConfig.from_yaml(find_config('session-config.yaml'))
# sess = Session.from_config(config=config)

# eq = sess.equipments[0]
# spec_defs = eq.spec_defs

# spec_def_df = eq.spec_defs_to(ScopedEquipment.IOFormats.df)

# eq_instances_df = eq.instances_to(ScopedEquipment.IOFormats.df)

# res = chunk_dataframe(eq_instances_df, axis=0, max_tokens=50)
# res = chunk_dataframe(eq_instances_df, axis=1, max_tokens=300)

# res = chunk_dataframe(eq_instances_df, axis=0, num_chunks=2)
# res = chunk_dataframe(eq_instances_df, axis=1, num_chunks=2)

# res = chunk_dataframe(eq_instances_df, axis=0, pct_list=[25, 25])