import argparse
import filecmp
import logging
import os
import shutil
from configparser import ConfigParser
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', required=True)
parser.add_argument('--log-level', choices=('INFO', 'DEBUG'), default='INFO')
args = parser.parse_args()

logging.basicConfig(
    level=getattr(logging, args.log_level),
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S'
)


def parse_config(config_path):
    logging.debug(f'Parse config: {config_path}')
    conf_parser = ConfigParser(allow_no_value=True, delimiters=('=',))
    conf_parser.optionxform = str
    with open(config_path, 'r') as config:
        conf_parser.read_file(config)
    config = {'backup_dest': None, 'paths': []}
    config['backup_dest'] = Path(conf_parser['settings']['backup_dest'])
    logging.debug(f'Parsed backup destination: {config["backup_dest"]}')
    for path in conf_parser['paths']:
        logging.debug(f'Parsed path to backup: {path}')
        config['paths'].append(Path(path))
    return config


def get_diff_files(dir_a, dir_b, files=None, dirs=None):
    if files is None:
        files = []
    if dirs is None:
        dirs = []
    dcmp = filecmp.dircmp(dir_a, dir_b)
    _files = dcmp.diff_files
    for lpath in dcmp.left_only:
        path_a = dir_a.joinpath(lpath)
        if path_a.is_dir():
            dirs.append((path_a, dir_b.joinpath(lpath)))
        else:
            _files.append(lpath)
    for file in _files:
        files.append((dir_a.joinpath(file), dir_b.joinpath(file)))
    for sub_dir in dcmp.subdirs.values():
        get_diff_files(Path(sub_dir.left), Path(sub_dir.right), files, dirs)
    return files, dirs


def main():
    logging.info('Starting backup script..')
    config = parse_config(args.config)
    backup_root = config['backup_dest']

    if not backup_root.exists():
        logging.debug(f'Creating backup destination dir: {backup_root}')
        os.makedirs(backup_root)

    for path in config['paths']:
        if path.is_file():
            backup_file = backup_root.joinpath(path.stem)
            if backup_file.exists() and filecmp.cmp(backup_file, path):
                logging.debug(f'File {backup_file} was not changed. Skipped..')
                continue
            logging.debug(f'Backup file {path} to {backup_root}')
            shutil.copy(path, backup_root)

        elif path.is_dir():
            backuped_dir = backup_root.joinpath(path.stem)
            if backuped_dir.exists():
                files, dirs = get_diff_files(path, backuped_dir)
                for src, dst in files:
                    logging.debug(f'Backup file {src} to {dst}')
                    shutil.copy(src, dst)
                for src, dst in dirs:
                    logging.debug(f'Backup dir {src} to {dst}')
                    shutil.copytree(src, dst)
            else:
                dst = backup_root.joinpath(path.stem)
                logging.debug(f'Backup dir {path} to {dst}')
                shutil.copytree(path, dst)
    logging.info('Making backup finished')


if __name__ == '__main__':
    main()
