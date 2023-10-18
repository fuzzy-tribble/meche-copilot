"""
Test the fillout_ws script
"""

from meche_copilot.esd_toolkit.get_results import get_results
from meche_copilot.esd_toolkit.update_from_worksheet import update_session_from_ws
from meche_copilot.esd_toolkit.schemas import Session, SessionConfig, ScopedEquipment
from meche_copilot.utils.config import load_config, find_config

config_box = load_config(find_config('config.yaml'))
config = SessionConfig(**config_box)

sess = Session.from_config(config=config)

sess.to_equipment_worksheet()

sess.update_from_worksheet()

# get results for each piece of equipment in the session
from rich.progress import Progress
with Progress() as progress:
  total_pieces = sum(len(eq.instances) * len(eq.spec_defs.keys()) for eq in sess.equipments)
  task = progress.add_task("[cyan]Processing...", total=total_pieces)
  # Run get_results and update the progress bar
  for progress_update, message in sess.get_results():
      progress.update(task, advance=progress_update, description=message)

from tests._test_data.test_data import equipments
eq1_dict = equipments[0]
eq2_dict = equipments[1]
# eq_json = json.dumps(eq_dict)
eq1 = ScopedEquipment(**eq1_dict)
eq2 = ScopedEquipment(**eq2_dict)
sess.equipments = [eq1, eq2]

sess.to_equipment_masterlist()