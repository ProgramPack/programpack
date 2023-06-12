#!/usr/bin/env python3
from sys import argv as args
from os import system as execute
from tempfile import gettempdir as get_temp_dir
import programpack as propack

def pull_from_git():
    execute(f'''cd {get_temp_dir()};
git clone https://github.com/ProgramPack/programpack.git -b experimental && mv programpack programpack-exp-branch;
cd programpack-exp-branch;
make sinstall && make sclean;
cd ..;
true && rm -rf programpack-exp-branch;''')

try: argv1 = args[1]
except IndexError: argv1 = None
try: argv2 = args[2]
except IndexError: argv2 = None
try: argv3 = args[3]
except IndexError: argv3 = None
try: argv4 = args[4]
except IndexError: argv4 = None
try: argv5 = args[5]
except IndexError: argv5 = None
try: argv6 = args[6]
except IndexError: argv6 = None
try: argv6 = args[7]
except IndexError: argv7 = None

help_message = '''--- ProgramPack ---
Commands:
    help
        Display this message
    run <fn> [--disable-icon-update] [--virtual]
        Run file by given name.
        --disable-icon-update:
        Do not update the icon
        --virtual:
        Will execute in virtual environment.
        May cause compatibility issues.
    convert <fn> [--virtual]
        Convert file to executable (linux) by given name.
        `chmod`'s the file and adds a shebang
        --virtual:
        Enable virtual environment for this file
    deconvert <fn>
        Will attempt to remove the shebang(s) from given file
    create <source> <destination>
        Create archive from directory name
    pull
        Update `ProgramPack` to latest version
    version
        See current version
    manifest <fn>
        Print manifest of file
    hub
        hub download <name> <domain> <author> [output]
            Will download ProgramPack file by name, domain and author from hub.'''
verbose = ('--verbose' in args)

if 'help' in str(argv1):
    print(help_message)
elif argv1 == 'convert':
    if argv2: propack.convert_file_to_executable(argv2, virtual = ('--virtual' in args))
    else: print('usage: convert <filename>')
elif argv1 == 'deconvert':
    if argv2: propack.deconvert(argv2)
    else: print('usage: deconvert <filename>')
elif argv1 == 'run':
    if argv2:
        if not '--disable-icon-update' in args: program.update_icon(verbose = verbose)
        if argv2 == '--virtual': program = propack.PackedProgram(argv3)
        else: program = propack.PackedProgram(argv2)
        program.read()
        program.run(virtual = ('--virtual' in args))
        program.close()
    else: print('usage: run <filename>')
elif argv1 == 'create':
    if argv2 and argv3:
        propack.create_archive(argv2, argv3 or 'create')
    else:
        print('usage: create <source> <destination>')
elif argv1 == 'pull': pull_from_git()
elif argv1 == 'version': print('ProgramPack - Version {}'.format(propack.__version__))
elif argv1 == 'manifest':
    if argv2:
        print(propack.get_manifest(argv2), end = '')
elif argv1 == 'hub':
    if argv2:
        if argv2 == 'download':
            if argv3 and argv4 and argv5:
                propack.hub_download(argv3, argv4, argv5, argv6 or 'output.txt')
            else:
                print('usage: hub download <name> <domain> <author> [output]')
        else: print('Unknown hub command. See --help')
    else:
        print('usage: hub <download, ...> <>')
else:
    if len(args) <= 1: print('No args given. See --help.')
    else: print('Invalid arguments. See --help for more info.')
