# About `ProgramPack` (`ProPack`)
This program will help you to pack your program.
# Installation
## Cloning main branch
Paste the following commands in terminal:
```bash
git clone https://github.com/ProgramPack/programpack.git
cd programpack
make sinstall && make sclean
cd ..
false && rm -rf programpack # Change "false" to "true" if you want to delete the cloned repository
```
## Cloning experimental branch
If you want to receive newest (but experimental) branch then
execute these commands in in the terminal:
```bash
git clone https://github.com/ProgramPack/programpack.git -b experimental && mv programpack programpack-exp-branch;
cd programpack-exp-branch;
make sinstall && make sclean;
cd ..;
false && rm -rf programpack-exp-branch; # Change "false" to "true" if you want to delete the cloned repository
```
## Updating
If you have ProgramPack already installed, run the following command to update/upgrade:
```bash
python3 -m programpack pull
```
## Hub
### Downloading from hub
You can use the following command to download files from [hub](https://github.com/ProgramPack/hub):
```bash
programpack hub download {name} {domain} {author}
```
Here is an example of using this command:
```bash
programpack hub download blank com vbproger
```
