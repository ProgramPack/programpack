#!/usr/bin/env python3
from sys import argv as args
import programpack as propack

try: argv1 = args[1]
except IndexError: argv1 = None

if argv1:
    program = propack.PackedProgram(argv1)
    program.read()
    program.run()
    program.close()
else:
    print('No args given.')