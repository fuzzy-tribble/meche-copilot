import fitz
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

from meche_copilot.chains.helpers.mechanical_schedule_table_to_df import mechanical_schedule_table_to_df
from meche_copilot.pdf_helpers.get_pages_from_text import get_pages_from_text
from meche_copilot.utils.envars import OPENAI_API_KEY

eqs = ["hydronic pump", "energy recovery ventilator (erv)", "exhaust fan"]

chat = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, model="gpt-4")

# chroma_db = Chroma(embedding_function=OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY), persist_directory="data/.chroma_db")
# p34 = chroma_db.get(where={"page": 33})['documents'][0]
# p35 = chroma_db.get(where={"page": 34})['documents'][0]

## GET A LIST OF SCHEDULES FROM A PDF
import re
doc = fitz.open('data/demo-01/engineering_design_drawings.pdf')
scheds_and_pages = []
for p in doc:
    blocks = p.get_text_blocks()
    for b in blocks:
        if "SCHEDULE" in b[4] and len(b[4].split(' ')) < 10:
            scheds_and_pages.append((b[4], p.number))
doc.close()

scheds_and_pages

# STEP #1: Get SCHEDULE(S) FOR EQUIPMENT

# NOTE - may need to chunk "data" along new lines
scheds, pages = zip(*scheds_and_pages)

class EquipmentScheduleTitles(BaseModel):
    equipment_name: str = Field(description="Equipment name/type (eg. hydronic pump, exhaust fan, energy recovery ventilator")
    schedule_titles: List[str] = Field(description="Schedule table titles that match the equipment name. There may be 0 or more items in the list")
parser = PydanticOutputParser(pydantic_object=EquipmentScheduleTitles)
prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{query}\n{data}",
    input_variables=["query"],
    partial_variables={
        "format_instructions": parser.get_format_instructions(),
        "data": '\n\n'.join(scheds)
        }
)
eq_sch_titles: List[EquipmentScheduleTitles] = []
for eq in eqs:
    query = f"Match the relavent schedule(s) for the equipment type: {eq}"
    # NOTE: it may be useful to include examples of alt schedules, continuations, what are not examples of schedules, other names for equipment, etc
    _input = prompt.format_prompt(query=query)
    output = chat.predict(_input.to_string())
    eq_sch_titles.append(parser.parse(output))
eq_sch_titles

# STEP #2: Get the GET SCHEDULE ROWS (OR AT LEAST LAST ROW) AND REMARKS
sched_titles = eq_sch_titles[0].schedule_titles
class ScheduleMetadata(BaseModel):
    title: str = Field(description="equipment schedule table title (eg. EXAMPLE EQUIPMENT SCHEDULE, EXAMPLE EQUIPMENT SCHEDULE (CONT....), EXAMPLE EQUIPMENT SCHEDULE (ALTERNATE), etc")
    row_labels: List[str] = Field(description="schedule table row labels usually called SYMBOL or MARK (eg. VRF-1, SL-4)")
    remarks: str = Field(description="remarks or notes for the schedule table")
    # row_dict: Dict[str, Any] = Field(description="a dict representation of the data in the schedule table. The table_data_dict.keys() should be the mark/symbol in the first column of the table ")
parser = PydanticOutputParser(pydantic_object=ScheduleMetadata)
prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{query}\n{data}",
    input_variables=["query", "data"],
    partial_variables={
        "format_instructions": parser.get_format_instructions()
        }
)
sched_tables = []
doc = fitz.open('data/demo-01/engineering_design_drawings.pdf')
for sch_title in sched_titles:
    print(f"Getting metadata for schedule: {sch_title}")
    pages = get_pages_from_text(text=sch_title, doc=doc)
    assert len(pages) == 1
    page_blocks = doc[pages[0]].get_text_blocks()
    page_text_blocks = [b[4] for b in page_blocks]
    print(f"Using text blocks on pg: {pages[0]}")
    query = f"What are the row labels, and remarks for the table with title: {sch_title}?"
    print(f"Query: {query}")
    _input = prompt.format_prompt(query=query, data='\n\n'.join(page_text_blocks))
    output = chat.predict(_input.to_string())
    sched_tables.append(parser.parse(output))
    break
sched_tables
    # get row data (not headers) and remarks and notes
doc.close()

# NOTE: can get row data like this and ask llm and then compare???
# get row data
# erv_row_data = { key: [] for key in index}
# for block in row_blocks:
#     row_list = block.split('\n')
#     if row_list[0] in erv_row_data.keys():
#         erv_row_data[row_list[0]].extend(row_list[1:])

# STEP #3: GET THE MECH SCHEDULE DATA AS DF
sched_metadata = sched_tables[0]
title = sched_metadata.title
rows_labels = sched_metadata.row_labels
page_num = "34"
print(f"Getting mechanical schedule table data for: {title} on page: {page_num}")
df = mechanical_schedule_table_to_df(pdf_fpath='data/demo-01/engineering_design_drawings.pdf', title=title, last_row=rows_labels[-1], page=page_num)

# class MechanicalSchedules(BaseModel):
#     equipment_type: str = Field(description="the type of the equipment")
#     mechanical_schedules: List[ScheduleTable] = Field(description="the mechanical schedule tables for the equipment type (always includes 'SCHEDULE' and may include continued or alternate schedules)")

