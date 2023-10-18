import glob
import os
import atexit
from pathlib import Path
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.theme import Theme
from rich.progress import Progress
from loguru import logger
from dotenv import load_dotenv, find_dotenv

from meche_copilot.esd_toolkit.get_equipment import get_equipment
from meche_copilot.esd_toolkit.get_results import get_results
from meche_copilot.esd_toolkit.get_scope import get_scope
from meche_copilot.esd_toolkit.schemas import Esd
from meche_copilot.esd_toolkit.update_from_worksheet import update_esd_from_excel
from meche_copilot.esd_toolkit.validate_scope import validate_scope
from meche_copilot.utils.config import load_config, find_config

load_dotenv(find_dotenv())
# logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")

class CliInterface:
    def __init__(self, config=None):
        logger.info('Initializing CLI Interface')
        self.root_volume = os.getenv('ROOT_VOLUME', '.')
        self.cli_config = config or load_config(find_config('cli-config.yaml', self.root_volume))
        self.agent_config = load_config(find_config('agent-config.yaml', self.root_volume))
        self.console = Console(theme=Theme(self.cli_config.theme))

        if len(self.agent_config.agents) != 3:
            raise ValueError('There must be exactly 3 agents in the agent config file. A design spec reader, a submittal spec reader, and a spec comparator.')
        
        agent_names = [agent['name'] for agent in self.agent_config.agents]
        self.esd_info = Esd(
            generated_by=', '.join(agent_names),
            design_spec_reader_prompt_template=self.agent_config.agents[0].prompt_template,
            submittal_spec_reader_prompt_template=self.agent_config.agents[1].prompt_template,
            spec_comparator_prompt_template=self.agent_config.agents[2].prompt_template
        )
        atexit.register(self.save_state_file)
        
    def __del__(self):
        self.save_state_file()

    def save_state_file(self):
        try:
            self.esd_info.to_excel()
        except Exception as e:
            logger.error(f'Error saving state file: {e}')

    def run(self):
        self.console.print(self.cli_config.intro_prompt, style="info")
        
        # authenticate user (just getting a username for now)
        self.user_auth(style="input")
        
        # select a project from the default project folder
        self.select_project()

        # optionally load previously saved sate file if it exists
        self.load_prev()

        ready_to_fillout_report = 'n'
        while ready_to_fillout_report in ['n', 'no']:
            # if no project scope has been saved, validate the project folder contents and get the project scope
            if len(self.esd_info.project_scope) == 0:
                self.validate_project_folder_contents()
            
            # if no equipment has been saved, get the equipment
            if len(self.esd_info.equipment) == 0:
                self.get_equipment()

            self.esd_info.to_excel()
            
            self.console.print(self.cli_config.verification_prompt, style='input')
            self.console.print('Are you like to continue? (Y/n): ', style='input', end='')
            ready_to_fillout_report = input().lower() or 'y'
            if ready_to_fillout_report in ['y', 'yes']:
                self.generate_esd_report()

        self.console.print(self.cli_config.extro_prompt, style="info")

    def get_equipment(self):
        self.esd_info.equipment = get_equipment(self.esd_info)

    def generate_esd_report(self):
        self.console.print(f'Generating esd report...', style='input')
        with Progress() as progress:
            task = progress.add_task("[cyan]Processing...", total=100)
            # Run get_results and update the progress bar
            for progress_update, message in get_results(self.esd_info):
                progress.update(task, advance=progress_update, description=message)
        self.console.print(f'Done. Report saved to {self.esd_info.project_fpath + "/esd-report.xlsx"}', style='input')
    
    def load_prev(self):
        """
        Load a previous esd-report file one exists. If not, create a new one in the .esd folder of the project dir
        """
        esd_files = glob.glob(f"{self.esd_info.project_fpath}/esd-report-*.xlsx")
        if esd_files:
            self.console.print(f'Found {len(esd_files)} previously generated ESD Reports.', style="input")
            self.console.print('\n0. Create new esd report', style="input")
            for i, file in enumerate(esd_files, start=1):
                    self.console.print(f'{i}. {file}', style="input")
            selected_file = prompt('Enter the number of the state file you want to load or "0" to start a new one: ')
            if int(selected_file) == 0:
                self.console.print(f'Started a new ESD Report', style="input")
            else:
                self.esd_info = update_esd_from_excel(esd_files[int(selected_file) - 1])
                self.console.print(f'Loaded state file: {esd_files[int(selected_file) - 1]}', style="input")

    def select_project(self):
        default_project_folder = os.getenv('PROJECTS')
        project_folders = [str(p) for p in Path(default_project_folder).iterdir() if p.is_dir()]
        if len(project_folders) == 0:
            self.console.print(f'No projects found in {default_project_folder}. Please create a project and try again.', style="input")
            exit()
        elif len(project_folders) == 1:
            self.console.print(f'Found one project, autoselecting it: {project_folders[0]}', style="input")
            self.esd_info.project_fpath = project_folders[0]
            return
        else:
            self.console.print('Found multiple project folders, select one:', style="input")
        for i, folder in enumerate(project_folders, start=1):
            folder_name = Path(folder).name
            self.console.print(f'{i}. {folder_name}', style="input")
        self.console.print(f'Note: If you cannot find your project, make sure that it is in the default project folder: {default_project_folder}', style="input")
        selected_project = prompt('Enter the number of your project: ', completer=WordCompleter(project_folders))
        self.esd_info.project_fpath = project_folders[int(selected_project) - 1]
    
    def validate_project_folder_contents(self):
        self.console.print('Validating project folder contents...', style="input")

        try:
            os.path.exists(Path(self.esd_info.project_fpath) / 'design-specs')
            self.console.print(f'✔ Found design-specs folder', style='input')
            
            os.path.exists(Path(self.esd_info.project_fpath) / 'submittal-specs')
            self.console.print(f'✔ Found submittal-specs folder', style='input')
            
            scope_fpath = Path(self.esd_info.project_fpath) / 'scope.xlsx'
            os.path.exists(scope_fpath)
            self.console.print(f'✔ Found scope.xlsx file', style='input')
            
            self.console.print('Validating ref files in scope exist in project folder...') 
            project_scope = get_scope(scope_fpath)
            validate_scope(project_scope, self.esd_info.project_fpath)
            self.esd_info.project_scope = project_scope
            self.console.print(f'✔ Found all ref files from scope', style='input')
        except Exception as e:
            self.console.print(f'Encountered an error while validating scope.xlsx: {e}\nPlease correct it and try again.', style="input")
            exit()

    def user_auth(self, style):
        self.console.print('Enter your username: ', style=style, end="")
        self.esd_info.reviewed_by = input()

if __name__ == "__main__":
    cli = CliInterface()
    cli.run()
