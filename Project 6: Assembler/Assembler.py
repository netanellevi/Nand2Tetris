import sys
import os
import re

MIN_ARGS = 1
NO_FILE = 1  # exit code for missing argument of file
ASM_EXT = '.asm'
NAME_POS = 0  # position of 'name' in file path
OUTFILE_NAME_FORMAT = '{path}//{name}.hack'  # pattern for saving file
SIXTEEN_BITS = "{0:016b}"  # 16 bits representation
NINE_BITS = "{0:09b}"  # 9 bits representation
THREE_BITS = "{0:03b}"  # 3 bits representation
A_INSTRUCTION_PREFIX = '@'
C_INSTRUCTION_PATTERN = '(?:(?P<dest>.*)=)?(?P<comp>[^;]*)(?:;(?P<jump>.*))?'
DEST_GROUP_NAME = 'dest'
COMP_GROUP_NAME = 'comp'
JUMP_GROUP_NAME = 'jump'

dest_dict = {None: '000', 'M': '001', 'D': '010', 'MD': '011', 'A': '100', 'AM': '101', 'AD': '110', 'AMD': '111'}
jump_dict = {None: '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011', 'JLT': '100', 'JNE': '101', 'JLE': '110',
             'JMP': '111'}
comp_dict = {'0': '0101010', '1': '0111111', '-1': '0111010', 'D': '0001100', 'A': '0110000', '!D': '0001101',
             '!A': '0110001', '-D': '0001111', '-A': '0110011', 'D+1': '0011111', 'A+1': '0110111', 'D-1': '0001110',
             'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011', 'A-D': '0000111', 'D&A': '0000000', 'D|A': '0010101',
             'M': '1110000', '!M': '1110001', '-M': '1110011', 'M+1': '1110111', 'M-1': '1110010', 'D+M': '1000010',
             'D-M': '1010011', 'M-D': '1000111', 'D&M': '1000000', 'D|M': '1010101'}
base_symbol_table = {'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4, 'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4,
                     'R5': 5, 'R6': 6, 'R7': 7, 'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11, 'R12': 12, 'R13': 13, 'R14': 14,
                     'R15': 15, 'SCREEN': 16384, 'KBD': 24576}


def parse_line(line, symbol_table, cur_var_idx):
    if line[0] == A_INSTRUCTION_PREFIX:
        if not line[1:].isdigit():
            symbol = line[1:]
            if symbol not in symbol_table:
                symbol_table[symbol] = cur_var_idx
                cur_var_idx += 1
            return SIXTEEN_BITS.format(symbol_table[symbol]), cur_var_idx
        return SIXTEEN_BITS.format(int(line[1:])), cur_var_idx
    else:
        c_instruction = re.compile(C_INSTRUCTION_PATTERN)
        matcher = c_instruction.fullmatch(line)
        dest = dest_dict[matcher.group(DEST_GROUP_NAME)]
        comp = comp_dict[matcher.group(COMP_GROUP_NAME)]
        jump = jump_dict[matcher.group(JUMP_GROUP_NAME)]
        return '111' + comp + dest + jump, cur_var_idx


def assemble(asm_file, hack_file):
    cur_line = 0
    cur_var_idx = 16
    symbol_table = base_symbol_table.copy()
    for line in asm_file:
        line = line.split("//")[0]  # trimming comment
        line = line.replace(" ", "").replace("\n", "")  # trimming whitespaces
        if not line:
            continue
        elif line[0] == '(':  # label
            label = line[1:-1]
            if label not in symbol_table:
                symbol_table[line[1:-1]] = cur_line
        else:
            cur_line += 1

    asm_file.seek(0)
    for line in asm_file:
        line = line.split("//")[0]  # trimming comment
        line = line.replace(" ", "").replace("\n", "")  # trimming whitespaces
        if not line or line[0] == '(':
            continue
        code_line, cur_var_idx = parse_line(line, symbol_table, cur_var_idx)
        hack_file.write(code_line + '\n')


if __name__ == '__main__':
    if len(sys.argv) < MIN_ARGS + 1:
        print('no file to assemble')
        sys.exit()
    path = os.path.abspath(sys.argv[1])
    if os.path.isdir(path):
        paths = list(map(lambda f: '{}//{}'.format(path, f), filter(lambda x: x.endswith(ASM_EXT), os.listdir(path))))
        out_dir = path
    else:
        paths = [path]
        out_dir = os.path.dirname(path)
    for path in paths:
        name = os.path.splitext(os.path.basename(path))[NAME_POS]
        with open(path, 'r') as infile, open(OUTFILE_NAME_FORMAT.format(path=out_dir, name=name), 'w') as outfile:
            assemble(infile, outfile)
