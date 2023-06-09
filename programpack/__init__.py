#!/usr/bin/env python3
import zipfile
import logging
from json import loads, dumps
from tempfile import NamedTemporaryFile as TempFile, gettempdir
from os.path import sep, join, basename, dirname, abspath, relpath, expanduser
from os import chmod, remove, makedirs as mkdir, listdir, chdir
from subprocess import run
from shutil import rmtree, move as move_file, make_archive as mkzip
from hashlib import sha256
from platform import system
from warnings import warn
from requests import get as r_get

__all__ = [
    'PackedProgram', 'convert_file_to_executable', 'deconvert', 'create_archive'
]
__version__ = '0.0.1'

shebang           = b'#!/usr/bin/env -S python3 -m programpack run\n'
shebang_v         = b'#!/usr/bin/env -S python3 -m programpack run --virtual\n'
_empty            = ''
_emptyb           = b''
_os               = system().strip().lower()
_server           = 'https://github.com/ProgramPack/hub'
_request_base     = '/raw/main/apps/'
_server_p_rbase   = '{}{}'.format(_server, _request_base)

def _get_text(url): return str(r_get(url).text)
def _get_json(url): return loads(_get_text(url).strip())
def _decode(b: bytes or bytearray) -> str: return b.decode('utf-8')
def _PropertyBlocked(): raise RuntimeError('Property is privated; blocked')
def _get_file_sha256(filename: str = ''):
    current_hash = sha256(usedforsecurity = False)
    buffer_size = 65536
    with open(filename, 'rb+') as f:
        while True:
            data = f.read(buffer_size)
            if not data: break
            current_hash.update(data)
    return current_hash.hexdigest()
def _getcachedir() -> str:
    cache_directory = ''
    if _os == 'linux' or _os == 'darwin': cache_directory = expanduser('~/.cache')
    else: cache_directory = r'C:\Windows\Temp\Cached'
    mkdir(cache_directory, exist_ok = True)
    return cache_directory

class PackedProgram:
    tempdir = gettempdir()
    resfold = 'Resources' + sep
    def __init__(self, archive_name: str):
        self.original_name = archive_name
        self.archive = zipfile.ZipFile(archive_name)
        self.tmpresfold = join(self.tempdir, self.resfold)
        self.call_args = []
    def read(self):
        '''Read data from archive'''
        self.manifest = loads(_decode(self.archive.read('manifest.json')))
        self.main_file = self.manifest['mainfile']
        self._setup_options()
    def _setup_options(self):
        '''Internal function'''
        m = self.manifest # Manifest
        m_res = m.get('resources_folder')
        m_icon_path = m.get('icon')

        self.icon_path = False

        if m_res: self.resfold = basename(m_res) + sep
        if m_icon_path: self.icon_path = basename(m_icon_path)
    def read_main_file(self):
        '''Return contents of the mainfile'''
        return self.archive.read(self.main_file)
    def read_resources(self) -> dict:
        '''Read "Resources" folder and return dictionary'''
        warn(
            'Function "read_resources" may be deprecated in future',
            DeprecationWarning
        )
        resources_dict = {}
        for resource in self.archive.namelist():
            if resource.startswith(self.resfold):
                resources_dict[resource.replace(self.resfold, '', 1)] = {
                    'path': resource,
                    'content': self.archive.read(resource)
                }
        return resources_dict
    def generate_unique_id(self):
        '''Generate unique identifier'''
        return self.manifest['author'] + '.' + self.manifest['name']
    def run(self, w_resources: bool = True, autocall: bool = True, delete: bool = True, virtual: bool = False):
        '''Execute ProgramPack file'''
        with TempFile(mode = 'w+', delete = False) as tempf:
            tempf_name = tempf.name
            with open(tempf_name, 'wb+') as f:
                f.write(self.read_main_file())
                del f
            chmod(tempf_name, 0o777)
        args = [tempf_name]
        args.extend(self.call_args)
        if w_resources:
            tmpresfold_n = join(self.tmpresfold, self.generate_unique_id())
            mkdir(tmpresfold_n, exist_ok = True)
            for current_file in self.archive.namelist():
                if current_file.startswith(self.resfold):
                    dest = join(tmpresfold_n, current_file.removeprefix(self.resfold))
                    if current_file.endswith(sep): mkdir(dest, exist_ok = True)
                    else:
                        self.archive.extract(current_file, tmpresfold_n)
                        move_file(join(tmpresfold_n, current_file), join(tmpresfold_n, dest))
                        rmtree(join(tmpresfold_n, 'Resources'), ignore_errors = True)
                del current_file
            args.append(tmpresfold_n)
        if autocall:
            if virtual:
                chdir(tmpresfold_n)
                run(args)
            else:
                chdir(expanduser('~'))
                run(args)
        if delete:
            remove(tempf_name)
            rmtree(tmpresfold_n, True)
    def close(self):
        '''Close current file'''
        rmtree(self.tmpresfold, True)
        self.archive.close()
        self.closed = property(lambda: True) # , _PropertyBlocked()
    def update_icon(self, _clean: bool = False, verbose: bool = False) -> bool:
        '''Read file icon (if exists) and update it if needed'''
        if not self.icon_path: return False
        data = self.archive.read(self.icon_path)
        if verbose: logging.debug(f'Icon path: {self.icon_path}')
        with TempFile(mode = 'wb+', delete = False) as tempf:
            tempf.write(data)
            tempf_name = tempf.name
            tempf.name = (
                join(
                    _getcachedir(), 
                    'icon_' + _get_file_sha256(tempf_name)
                )
                + '.png'
            )
            if verbose: logging.debug(f'Old location of `tempf`: {tempf_name}')
            if verbose: logging.debug(f'New location of `tempf`: {tempf.name}')
            move_file(tempf_name, tempf.name)
            del tempf_name
            source_filename = self.original_name.strip() or 'unknown'
            cmd = f'gio set -t string {source_filename} metadata::custom-icon file://{tempf.name}'
            if verbose: logging.debug(f'Command: `{cmd}`')
            run(
                [
                    cmd
                ],
                shell = True,
                executable = '/usr/bin/bash'
                )
            if verbose: logging.info('Command finished')
        if _clean:
            warn(
                'Consider setting _clean to False because after updating icon will disappear',
                 ResourceWarning
            )
            remove(tempf.name)
        return True
def generate_unique_id_local(name: str = 'unnamed', domain: str = 'com', author: str = 'unknown'): return '{}.{}.{}'.format(domain, author, name)
def convert_file_to_executable(file_name: str = '', virtual: bool = False):
    '''Make the file executable by other programs'''
    chmod(file_name, 0o777)
    with open(file_name, 'rb+') as f: data = f.read()
    with open(file_name, 'wb+') as f: f.write((shebang_v if virtual else shebang) + data)
def deconvert(file_name):
    '''Remove shebang from file'''
    with open(file_name, 'rb+') as f: data = f.read()
    with open(file_name, 'wb+') as f: f.write(data.replace(shebang, _emptyb).replace(shebang_v, _emptyb))
def create_archive(source_directory: str = '', archive_name: str = '', password: str = None, convert: bool = False):
    archive_name = basename(archive_name).removesuffix('.zip')
    chdir(source_directory)
    mkzip(abspath(join('..', archive_name)), 'zip', source_directory)
    if password:
        password = (password or '').encode('utf-8', errors = 'ignore')
        zipfile.ZipFile(archive_name).setpassword(password)
    if convert: convert(archive_name)
def get_manifest(file_name: str = '') -> dict or bool:
    if not file_name: return False
    program = PackedProgram(str(file_name).strip())
    program.read()
    return program.manifest
def hub_get_id_by(name: str, domain: str, author: str, *args, **kwargs): return _server_p_rbase + generate_unique_id_local(name, domain, author, *args, **kwargs) + '.json'
def hub_get_meta(name: str, domain: str, author: str): return _get_json(hub_get_id_by(name, domain, author))
def hub_download_s(name: str, domain: str, author: str): return _get_text(hub_get_meta(name, domain, author)['link'])
def hub_download(name: str, domain: str, author: str, output: str = 'download.propack'):
    data = hub_download_s(name, domain, author)
    with open(str(output).strip(), 'w+') as f:
        f.write(data)
    chmod(output, 0o777)
