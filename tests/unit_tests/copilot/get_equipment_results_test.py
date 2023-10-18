"""
Test get equipment results
"""

import pytest

@pytest.mark.skip(reason="Not implemented")
def test_get_equipment_results():
  pass

# import json
# import pandas as pd
# import copy
# from meche_copilot.schemas import *
# from tests._test_data.test_data import equipments

# eq1_dict = equipments[0]
# eq2_dict = equipments[1]
# # eq_json = json.dumps(eq_dict)
# eq1 = ScopedEquipment(**eq1_dict)
# eq2 = ScopedEquipment(**eq2_dict)

# # get spec lookup data for equipment (these agents need just value, page for each spec)

# # results for source A
# eq_copy = copy.deepcopy(eq1)
# for inst in eq_copy.instances:
#     del inst.sourceB
#     for spec in inst.spec_results:
#         del spec.final_result
#         del spec.resB
#         del spec.resA.validation
#         del spec.resA.annotation
# empty_val_pg_srcA = eq_copy.json(exclude_unset=True)
# empty_val_pg_srcA

# # results for source B - same


# # what would comparator agent input and result look like? compares two vals
# empty_annots_final_res = copy.deepcopy(eq1)
# for inst in empty_annots_final_res.instances:
#   for spec in inst.spec_results:
#     if spec.resA.validation is None or spec.resB.validation is None:
#       del spec
#     else:
#       del spec.resA.validation
#       del spec.resA.page
#       del spec.resB.validation
#       del spec.resB.page
# empty_annots_final_res.json(exclude_unset=True)