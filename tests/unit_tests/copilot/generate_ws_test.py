"""
Tests generate-ws
"""
import pytest
import os
from meche_copilot.cli.generate_ws import GenerateWorkskeetCli
from meche_copilot.schemas import Session, SessionConfig
from meche_copilot.utils.config import load_config, find_config

def test_init_session():
    """
    Test that we can create a valid session
    """
    sess_config_box = load_config(find_config('session-config.yaml'))
    sess_config = SessionConfig(**sess_config_box)
    sess = Session.from_config(config=sess_config)
    assert sess is not None

def test_session_reads_equipment():
    """
    Test that we can read equipment from config
    """
    sess_config_box = load_config(find_config('session-config.yaml'))
    sess_config = SessionConfig(**sess_config_box)
    sess = Session.from_config(config=sess_config)
    assert len(sess.equipments) > 0

def test_run_generate_ws_writes_to_excel():
    """
    Test that we run generate-ws without error and that it writes to excel
    """
    cli = GenerateWorkskeetCli()
    with pytest.raises(SystemExit) as e:
        cli.run()
        assert e.value.code == 0
    output_fpath = cli.sess.config.working_fpath / "worksheet.xlsx"
    assert os.path.exists(output_fpath)