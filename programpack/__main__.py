#!/usr/bin/env python3
from sys import argv as args
import programpack as propack

try: argv1 = args[1]
except IndexError: argv1 = None
try: argv2 = args[2]
except IndexError: argv2 = None

if argv1 == 'convert':
    if argv2: propack.convert_file_to_executable(argv2)
elif argv1 == 'run':
    if argv2:
        program = propack.PackedProgram(argv2)
        program.read()
        program.run()
        program.close()
else:
    print('No args given.')
