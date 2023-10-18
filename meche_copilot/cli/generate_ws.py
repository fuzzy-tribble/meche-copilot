import os
import sys
from pathlib import Path
from rich.console import Console
from rich.theme import Theme
from loguru import logger
from dotenv import load_dotenv, find_dotenv

from meche_copilot.schemas import Session
from meche_copilot.utils.config import load_config, find_config

load_dotenv(find_dotenv())

class GenerateWorkskeetCli:
    """
    The main entry point for the copilot-generate-ws CLI script
    """
    def __init__(self, config=None):
        logger.info(f'Initializing...')

        self.root_volume = Path(os.getenv('PROJECT_ROOT'))
        
        # setup cli
        self.cli_config = config or load_config(find_config('cli-config.yaml'))
        self.console = Console(theme=Theme(self.cli_config.theme))
        self.cli_config = self.cli_config.generate_ws

        # get sess configs
        self.sess_config = load_config(find_config('session-config.yaml'))
        self.sess = None

    def run(self):
        self.console.print(self.cli_config.intro_prompt, style="intro")

        # create sess object then write to excel
        try: 
            self.sess = Session.from_config(config=self.sess_config)
            self.sess.to_equipment_worksheet()
        except Exception as e:
            logger.error(f'Error creating session: {e}', exc_info=True)
            self.console.print(f'Unable to create session: {e}\nFix and retry', style="error")
            sys.exit(1)

        self.console.print(self.cli_config.outtro_prompt, style="outtro")
        sys.exit(0)

def main():
    cli = GenerateWorkskeetCli()
    cli.run()

if __name__ == "__main__":
    main()
