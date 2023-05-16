#!/usr/bin/env python3
from sys import argv as args
import programpack as propack

try: argv1 = args[1]
except IndexError: argv1 = None
try: argv2 = args[2]
except IndexError: argv2 = None
try: argv3 = args[3]
except IndexError: argv3 = None

help_message = '''--- ProgramPack ---
Commands:
    help
        Display this message
    run <fn> [noupdate]
        Run file by given name. If `noupdate` == `false` or `0`
        then it will not update the icon
    convert <fn>
        Convert file to executable (linux) by given name.
        `chmod`'s the file and adds a shebang
    deconvert <fn>
        Will attempt to remove the shebang from given file'''

if 'help' in argv1:
    print(help_message)
elif argv1 == 'convert':
    if argv2: propack.convert_file_to_executable(argv2)
    else: print('usage: convert <filename>')
elif argv1 == 'deconvert':
    if argv2: propack.deconvert(argv2)
    else: print('usage: deconvert <filename>')
elif argv1 == 'run':
    if argv2:
        program = propack.PackedProgram(argv2)
        program.read()
        if not str(argv3).lower().strip() in ('false', '0'): program.update_icon()
        program.run()
        program.close()
    else: print('usage: run <filename>')
else:
    print('No args given.')
