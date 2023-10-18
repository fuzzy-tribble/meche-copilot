import copy
import json
from typing import List, Tuple
from loguru import logger

from meche_copilot.schemas import ScopedEquipment
from meche_copilot.chains.lookup_specs_chain import AnalyzeSpecsChain
from meche_copilot.chains.read_submittal_chain import get_compare_specs_chain
from meche_copilot.pdf_helpers.get_text_bounding_box import get_text_bounding_box

# TODO - change data prep so not copying and deleting...yuck

def get_equipment_results(eq: ScopedEquipment, selected_instances: List[str] = None):
  """
  Get results for a piece of equipment

  First get value, page for source A
  Validate page for source A

  Then get value, page for source B
  Validate page for source B

  Compare values for source A and source B and make annotations and update final result
  """

  # get a json representation of equipment with its list of specs that the agent will use be filling in
  empty_val_pg_srcA, empty_val_pg_srcB = get_spec_lookup_data(eq)
  lookup_specs_chain = None
  compare_specs_chain = None
  val_pg_val_srcA = None
  val_pg_val_srcB = None
  annots_final_res = None

  # try looking up spec data for source A
  try: 
    # get lookup specs chain
    if lookup_specs_chain is None:
      lookup_specs_chain = AnalyzeSpecsChain()

    # get resA results and validate value, page
    val_pg_srcA = lookup_specs_chain(
      empty_val_pg=empty_val_pg_srcA,
      source=eq.sourceA.dict()
      )
    val_pg_val_srcA = get_spec_page_validations(val_pg_srcA, eq.sourceA.ref_docs)
  except Exception as e:
    logger.error(f'Error getting results for source A: {e}', exc_info=True)
  

  # try looking up spec data for source B
  try:
    # get lookup specs chain
    if lookup_specs_chain is None:
      lookup_specs_chain = get_lookup_specs_chain()

    # get resB results and validate value, page 
    val_pg_srcB = lookup_specs_chain.run(
      empty_val_pg=empty_val_pg_srcB,
      source=eq.sourceB.dict()
    )
    val_pg_val_srcB = get_spec_page_validations(val_pg_srcB, eq.sourceB.ref_docs)
  except Exception as e:
    logger.error(f'Error getting results for source B: {e}', exc_info=True)

  # try comparing resA and resB values that are valid and make annotations
  if val_pg_val_srcA is not None and val_pg_val_srcB is not None:
    try:
      # compare resA and resB values that are valid and make annotations
      compare_specs_chain = get_compare_specs_chain()
      empty_annots_final_res = get_compare_specs_data(eq)
      annots_final_res = compare_specs_chain.run_chain(
        empty_annots_final_res=empty_annots_final_res,
        sourceA=eq.sourceA.dict(),
        sourceB=eq.sourceB.dict()
      )

    except Exception as e:
      logger.error(f'Error comparing results for source A and source B: {e}', exc_info=True)
  else:
    logger.warning(f'Not running compare specs chain because val_pg_val_srcA or val_pg_val_srcB is None')

  # return scoped_equipment with results from specA and specB results and final result
  new_scoped_equipment = copy.deepcopy(eq)
  return new_scoped_equipment

def get_spec_lookup_data(eq: ScopedEquipment) -> Tuple[str, str]:
  empty_eq_string = eq.instances_to(ScopedEquipment.IOFormats.csv_str)

  return empty_eq_string, empty_eq_string

def get_compare_specs_data(eq: ScopedEquipment) -> str:
  empty_annots_final_res = copy.deepcopy(eq)
  for inst in empty_annots_final_res.instances:
    for spec in inst.spec_results:
      if spec.resA.validation is None or spec.resB.validation is None:
        del spec
      else:
        del spec.resA.validation
        del spec.resA.page
        del spec.resB.validation
        del spec.resB.page
  return empty_annots_final_res.json(exclude_unset=True)

def get_spec_page_validations(val_pg: json, ref_docs: List[str]) -> json:
  """
  Valid if a single instance of a spec is found in a page
  """
  for inst in val_pg['instances']:
    for spec in inst['spec_results']:
      # validate page
      spec['resA']['validation'] = get_text_bounding_box(spec['resA']['page'], ref_docs)
      spec['resB']['validation'] = get_text_bounding_box(spec['resB']['page'], ref_docs)
  return val_pg