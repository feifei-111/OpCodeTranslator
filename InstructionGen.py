import dataclasses
import dis
import opcode
from typing import Optional, Any
import sys, types

from dy2static_call import dy2static_call


LOADS = [
    "LOAD_FAST",
    "LOAD_GLOBAL",
    "LOAD_METHOD",
    "LOAD_NAME",
    "LOAD_CLASSDETEF",
    "LOAD_DETEF",
    "LOAD_CLOSURE",
    "LOAD_ATTR",
    # "LOAD_CONST"  # not needed
]

ADD_GLOBAL_NAMES = {
    "dy2static_call" : [-1, dy2static_call],
}

class InstructionTranslator:
    def __init__(self, frame, code_options):
        self.frame = frame
        self.instrs = list(map(convert_instruction, dis.get_instructions(frame.f_code)))
        self.code_options = code_options
        self.p = 0                  # a pointer

        global ADD_GLOBAL_NAMES
        for key, val in ADD_GLOBAL_NAMES.items():
            _, obj = val
            if key in frame.f_globals.keys():
                raise(f"name {key} already exists!!!")
            arg = len(code_options["co_names"])
            ADD_GLOBAL_NAMES[key][0] = arg
            code_options["co_names"].append(key)
            frame.f_globals[key] = obj

    def current_instr(self):
        return self.instrs[self.p]

    def p_next(self, n=1):
        self.p += n

    def p_prev(self, n=1):
        self.p -= n

    def p_seek(self, n=0):
        self.p = n

    def find_next_instr(self, names):
        if isinstance(names, str):
            names = [names]
        found = False
        start = self.p + 1
        end = len(self.instrs)
        for i in range(start, end):
            if self.instrs[i].opname in names:
                found  = True
                self.p_seek(i)
                break
        return found

    def insert_instr(self, instr):
        self.instrs.insert(self.p + 1, instr)
    
    def insert_instr_list(self, instr_list):
        part1 = self.instrs[0:self.p+1]
        part2 = self.instrs[self.p+1:]
        self.instrs = part1 + instr_list + part2

    def run(self):
        self.transform_loads()
        return self.instrs

    def transform_loads(self):
        self.p_seek(-1)
        while self.find_next_instr(LOADS):
            to_be_insert = InstrGen(self).gen_for_loads()
            if to_be_insert:
                self.insert_instr_list(to_be_insert)
                self.p_next(len(to_be_insert))


class InstrGen:
    def __init__(self, instr_transformer):
        self.instr_trans = instr_transformer
        self.frame = instr_transformer.frame

    def gen_for_loads(self):
        instr = self.instr_trans.current_instr()
        if instr.is_generated:
            return None
        arg = ADD_GLOBAL_NAMES["dy2static_call"][0]
        instrs = [
            gen_instr("LOAD_GLOBAL", arg= arg, argval="dy2static_call"),
            gen_instr("ROT_TWO"),
            gen_instr("CALL_FUNCTION", arg=1, argval=1)
        ]
        return instrs

class _NotProvided:
    pass

def gen_instr(name, arg=None, argval=_NotProvided, gened=True):
    if argval is _NotProvided:
        argval = arg
    return Instruction(
        opcode=dis.opmap[name], opname=name, arg=arg, argval=argval, is_generated=gened
    )

@dataclasses.dataclass
class Instruction:
    opcode: int
    opname: str
    arg: Optional[int]
    argval: Any
    offset: Optional[int] = None
    starts_line: Optional[int] = None
    is_jump_target: bool = False
    is_generated: bool = True

    def __hash__(self):
        return id(self)

def convert_instruction(i: dis.Instruction):
    return Instruction(
        i.opcode,
        i.opname,
        i.arg,
        i.argval,
        i.offset,
        i.starts_line,
        i.is_jump_target,
        is_generated=False
    )

def op_arg_space(op):
    if op in opcode.hasconst:
        return "co_consts"
    elif op in opcode.hasname:
        return "co_names"
    elif op in opcode.haslocal:
        return "co_varnames"
    elif op in opcode.hasfree:
        return "co_cellvars + co_freevars"

    elif op in opcode.hasjrel:
        return "jrel"
    elif op in opcode.hascompare:
        return "compare"
    elif op == opcode.opmap['FORMAT_VALUE']:
        return "format value"
    elif op == opcode.opmap['MAKE_FUNCTION']:
        return "make function"

