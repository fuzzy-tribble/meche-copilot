import argparse
from distutils.command import clean
import os
import sys
import shutil
import glob

# TODO - remove .esd/* from project folders?

def clean_project():
    parser = argparse.ArgumentParser(description='Clean component build artifacts and caches.')
    parser.add_argument('component', nargs='?', default='all', help='The component to clean (caches, logs or all))')
    # parser.add_argument('--test', action='store_true', help='Clean test artifacts only')
    parser.add_argument('--mock', action='store_true', help='Mock clean (see what files/folders would be removed)')

    args = parser.parse_args()

    project_root_dir = os.getcwd()
    fpath_test = os.path.join(project_root_dir, 'src/')
    assert os.path.exists(fpath_test), f'{fpath_test} does not exist. Make sure you are running build/clean from the root project directory.'

    if args.component == 'caches':
        clean_caches(project_root_dir, args)
    elif args.component == 'logs':
        clean_logs(project_root_dir, args)
    elif args.component == 'all':
        clean_logs(project_root_dir, args)
        clean_caches(project_root_dir, args)
    else:
        parser.print_help()
        sys.exit(1)


def clean_logs(project_root_dir, args):
    files_and_dirs_to_remove = ['logs/*.log', 'logs/*.log.*']
    rm_files_and_folders(files_and_dirs_to_remove, project_root_dir, args)

def clean_caches(project_root_dir, args):
    files_and_dirs_to_remove = ['**/__pycache__', '**/*.egg-info', '**/.pytest_cache', '**/.coverage', 'esd-*']
    
    print('Cleaning caches...')
    rm_files_and_folders(files_and_dirs_to_remove, project_root_dir, args)


def rm_files_and_folders(files_and_dirs_to_remove, project_root_dir, args):
    for path in files_and_dirs_to_remove:
        full_paths = glob.glob(os.path.join(project_root_dir, path), recursive=True)
        for full_path in full_paths:
            try:
                if os.path.isfile(full_path):
                    if not args.mock:
                        os.remove(full_path)
                    print(full_path)
                elif os.path.isdir(full_path):
                    if not args.mock:
                        shutil.rmtree(full_path)
                    print(full_path)
            except FileNotFoundError:
                print(f'{full_path} does not exist')
            except OSError as e:
                print(f'Error: {e.filename} - {e.strerror}.')
