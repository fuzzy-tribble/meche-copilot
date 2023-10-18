"""
Test open pdf on user machine (windows/mac/linux)
"""
import pytest
from meche_copilot.pdf_helpers.open_pdf import open_pdf

@pytest.mark.skip(reason="Not implemented")
def test_open_pdf_on_user_machine():
    pass

# # SCAFFOLD
# pdf_fpath = "test/test_data/input.pdf"
# page=0

# open_pdf(
#     pdf_fpath=pdf_fpath, 
#     page=page
# )