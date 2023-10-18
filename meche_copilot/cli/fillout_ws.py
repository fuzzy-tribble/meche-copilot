import os
import argparse
from typing import Optional, List
from pathlib import Path
from rich.console import Console
from rich.theme import Theme
from rich.progress import Progress
from loguru import logger
from dotenv import load_dotenv, find_dotenv

from meche_copilot.schemas import Session
from meche_copilot.utils.config import load_config, find_config
load_dotenv(find_dotenv())

class FilloutWorkskeetCli:
    def __init__(self, config=None, selected_equipments: List[str] = None, selected_equipment_instances: List[str] = None):
        logger.info(f'Initializing...')

        if selected_equipments is not None:
            logger.warning("Fillout sleect equipment types isn't implemented")
            raise NotImplementedError
        
        if selected_equipment_instances is not None:
            logger.warning("Fillout sleect equipment instances isn't implemented")
            raise NotImplementedError

        self.root_volume = Path(os.getenv('ROOT_VOLUME'))
        
        # setup cli
        self.cli_config = config or load_config(find_config('cli-config.yaml'))
        self.console = Console(theme=Theme(self.cli_config.theme))
        self.cli_config = self.cli_config.fillout_ws
        
        # get session configs
        self.sess_config = load_config(find_config('config.yaml'))
        self.session = None

    def run(self):
        self.console.print(self.cli_config.intro_prompt, style="intro")

        try: 
            self.sess = Session.from_config(config=self.sess_config)
            logger.info(f'Done getting esd from config')
            self.sess.update_from_worksheet()
            logger.info(f'Done updating esd from worksheet')

            # TODO - if design data and submittal data isn't in cache, run read design and read submittal chains

            self.console.print(f'Filling out worksheet...go get a 🍜...', style='info')
            with Progress() as progress:
                task = progress.add_task("[cyan]Processing...", total=100)
                # Run get_results and update the progress bar
                for progress_update, message in self.sess.get_results():
                    progress.update(task, advance=progress_update, description=message)
            self.console.print(f'Done filling out worksheet', style='input')

        except Exception as e:
            logger.error(f'Error creating esd object: {e}')
            self.console.print(f'Unable to create esd object: {e}\nFix and retry', style="error")
            exit(1)

        self.console.print(self.cli_config.outtro_prompt, style="outtro")
        exit(0)

def main():
    parser = argparse.ArgumentParser(description="Fill out worksheet CLI")

    group = parser.add_mutually_exclusive_group()
    
    # TODO - these are not required arguments

    group.add_argument('--equipment-type',
                        nargs='+',
                        metavar='selected_equipments',
                        type=str,
                        help='the equipment type(s) (worksheet tab name) to fill out (eg pump "cooling tower" fan)')

    group.add_argument('--equipment-instance',
                        nargs='+',
                        metavar='selected_equipment_instances',
                        type=str,
                        help='the equipment instance name(s) to fill out (eg. "pump-1")')

    args = parser.parse_args()

    # Convert the list of arguments to a set to ensure uniqueness
    selected_equipments = list(set(args.equipment_type)) if args.equipment_type else None
    selected_equipment_instances = list(set(args.equipment_instance)) if args.equipment_instance else None

    cli = FilloutWorkskeetCli(selected_equipments=selected_equipments, selected_equipment_instances=selected_equipment_instances)
    cli.run()

if __name__ == "__main__":
    main()