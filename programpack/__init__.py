#!/usr/bin/env python3
import zipfile
from json import loads, dumps
from tempfile import NamedTemporaryFile as TempFile, gettempdir
from os.path import sep, join
from os import chmod, remove, makedirs as mkdir
from subprocess import call
from shutil import rmtree

def _decode(b: bytes or bytearray) -> str: return b.decode('utf-8')
def _PropertyBlocked(): raise RuntimeError('Property is privated; blocked')

class PackedProgram:
    tempdir = gettempdir()
    resfold = 'Resources' + sep
    def __init__(self, archive):
        self.archive = zipfile.ZipFile(archive)
        self.tmpresfold = join(self.tempdir, self.resfold)
        self.call_args = []
    def read(self):
        '''Read data from archive'''
        self.manifest = loads(_decode(self.archive.read('manifest.json')))
        self.main_file = self.manifest['mainfile']
    def read_main_file(self): return self.archive.read(self.main_file)
    def read_resources(self):
        resources_dict = {}
        for resource in self.archive.namelist():
            if resource.startswith(self.resfold):
                resources_dict[resource.replace(self.resfold, '', 1)] = {
                    'path': resource,
                    'content': self.archive.read(resource)
                }
        return resources_dict
    def generate_unique_id(self): return self.manifest['author'] + '.' + self.manifest['name']
    def run(self, w_resources: bool = True, autocall: bool = True, delete: bool = True):
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
        if autocall: call(args)
        if delete:
            remove(tempf_name)
            rmtree(tmpresfold_n, True)
    def close(self):
        rmtree(self.tmpresfold, True)
        self.archive.close()
        self.closed = property(lambda: True) # , _PropertyBlocked()