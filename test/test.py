#!/usr/bin/env python3
import unittest, pydoc, zipfile
propack = pydoc.importfile('programpack/__init__.py')

class TestProgramPack(unittest.TestCase):
    def setUp(self): self.propack = propack
    def test_PackedProgram(self):
        program = self.propack.PackedProgram('test/testapp.propack')
        program.read()
        program.run()
        program.close()

        program = self.propack.PackedProgram('test/also_testing.propack')
        program.read()
        program.update_icon()
        program.run()
        program.close()

if __name__ == '__main__':
    unittest.main()