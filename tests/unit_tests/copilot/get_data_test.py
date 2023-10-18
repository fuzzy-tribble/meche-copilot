"""
Test that equipment to/from csv/df/string works as expected
"""

import pytest
from meche_copilot.schemas import *
from meche_copilot.utils.config import find_config

@pytest.fixture
def eq():
    config = SessionConfig.from_yaml(find_config('session-config.yaml'))
    sess = Session.from_config(config=config)
    eq_inst = sess.equipments[0]
    return eq_inst

def test_spec_defs_to_df(eq: ScopedEquipment):
    df = eq.spec_defs_to(ScopedEquipment.IOFormats.df)
    spec_defs = ScopedEquipment.spec_defs_from(input=df, input_format=ScopedEquipment.IOFormats.df)
    assert eq.spec_defs == spec_defs

@pytest.mark.skip(reason="TODO - fix bug")
def test_spec_defs_to_csv(eq: ScopedEquipment):
    csv_str = eq.spec_defs_to(ScopedEquipment.IOFormats.csv_str)
    spec_defs = ScopedEquipment.spec_defs_from(input=csv_str, input_format=ScopedEquipment.IOFormats.csv_str)
    assert eq.spec_defs == spec_defs

def test_eq_instances_to_df(eq: ScopedEquipment):
    df = eq.instances_to(ScopedEquipment.IOFormats.df)
    eq_instances = ScopedEquipment.instances_from(input=df, input_format=ScopedEquipment.IOFormats.df)
    assert eq.instances == eq_instances

@pytest.mark.skip(reason="TODO - fix bug")
def test_eq_instances_to_csv(eq: ScopedEquipment):
    csv_str = eq.instances_to(ScopedEquipment.IOFormats.csv_str)
    eq_instances = ScopedEquipment.instances_from(input=csv_str, input_format=ScopedEquipment.IOFormats.csv_str)
    assert eq.instances == eq_instances