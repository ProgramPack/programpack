#!/usr/bin/env python3
import unittest, pydoc, zipfile
from os import getcwd, chdir
from os.path import join as join_paths
propack = pydoc.importfile('programpack/__init__.py')

class TestProgramPack(unittest.TestCase):
    def setUp(self): self.propack = propack
    def test_PackedProgram(self):
        captured_dir = join_paths(getcwd())
        chdir(captured_dir)

        program = self.propack.PackedProgram('test/testapp.propack')
        program.read()
        program.run()
        program.close()

        chdir(captured_dir)

        program = self.propack.PackedProgram('test/also_testing.propack')
        program.read()
        program.update_icon()
        program.run()
        program.close()

if __name__ == '__main__':
    unittest.main()
