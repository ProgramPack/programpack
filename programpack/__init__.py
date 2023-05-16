#!/usr/bin/env python3
import zipfile
from json import loads, dumps
from tempfile import NamedTemporaryFile as TempFile, gettempdir
from os.path import sep, join, basename, dirname, relpath
from os import chmod, remove, makedirs as mkdir
from subprocess import run
from shutil import rmtree

shebang    = b'#!/usr/bin/env -S python3 -m programpack run\n'
_empty     = ''
_emptyb    = b''

def _decode(b: bytes or bytearray) -> str: return b.decode('utf-8')
def _PropertyBlocked(): raise RuntimeError('Property is privated; blocked')

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

        self.icon_path = 'icon'

        if m_res: self.resfold = basename(m_res) + sep
        if m_icon_path: self.icon_path = basename(m_icon_path)
    def read_main_file(self):
        '''Return contents of the mainfile'''
        return self.archive.read(self.main_file)
    def read_resources(self) -> dict:
        '''Read "Resources" folder and return dictionary'''
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
    def run(self, w_resources: bool = True, autocall: bool = True, delete: bool = True):
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
            res = self.read_resources()
            tmpresfold_n = join(self.tmpresfold, self.generate_unique_id())
            if res:
                mkdir(tmpresfold_n, exist_ok = True)
                for key in res:
                    value = res[key]
                    if key and value:
                        with open(join(tmpresfold_n, key), 'wb+') as f:
                            f.write(value['content'])
            args.append(tmpresfold_n)
        if autocall: run(args)
        if delete:
            remove(tempf_name)
            rmtree(tmpresfold_n, True)
    def close(self):
        '''Close current file'''
        rmtree(self.tmpresfold, True)
        self.archive.close()
        self.closed = property(lambda: True) # , _PropertyBlocked()
    def update_icon(self):
        '''Read file icon (if exists) and update it if needed'''
        data = self.archive.read(self.icon_path)
        with TempFile(mode = 'wb+') as tempf:
            tempf.write(data)
            tempf_name = tempf.name
            run([
                'gio',
                'set'
                '-t',
                'string',
                self.original_name or 'unknown',
                f'metadata::custom-icon',
                'file://{tempf_name}'
            ])
def convert_file_to_executable(file_name):
    '''Make the file executable by other programs'''
    chmod(file_name, 0o777)
    with open(file_name, 'rb+') as f: data = f.read()
    with open(file_name, 'wb+') as f: f.write(shebang + data)
def deconvert(file_name):
    '''Remove shebang from file'''
    with open(file_name, 'rb+') as f: data = f.read()
    with open(file_name, 'wb+') as f: f.write(data.replace(shebang, _emptyb))