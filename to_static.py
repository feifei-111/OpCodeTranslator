import contextlib
import collections
import paddle
import dis

from InstructionGen import InstructionTranslator, convert_instruction
from OpCodeGen import gen_new_opcode
from symbolic_trace import SymbolicTraceContext

CustomCode = collections.namedtuple("CustomCode", ["code"])


def to_static(func):
    def wrapped(*args, **kw):
        with Dy2staticGuard(eval_frame_callback):
            func(*args, **kw)
    return wrapped


def eval_frame_callback(frame):
    if frame.f_code.co_name == "caller":
        new_code = transform_opcode(frame)
        retval = CustomCode(new_code)
        return retval
    return None


@contextlib.contextmanager
def Dy2staticGuard(callback):
    with SymbolicTraceContext() as ctx:
        paddle.fluid.core.set_eval_frame(callback)
        yield
        paddle.fluid.core.set_eval_frame(None)
        SymbolicTraceContext().start_compile()


# can not use frame now, give obj instead temporarily
def transform_opcode(frame):
    # check definition of types.CodeType
    keys = [
        "co_argcount",
        "co_posonlyargcount",
        "co_kwonlyargcount",
        "co_nlocals",
        "co_stacksize",
        "co_flags",
        "co_code",
        "co_consts",
        "co_names",
        "co_varnames",
        "co_filename",
        "co_name",
        "co_firstlineno",
        "co_lnotab",
        "co_freevars",
        "co_cellvars",
    ]

    code_options = {}
    for k in keys:
        val = getattr(frame.f_code, k)
        if isinstance(val, tuple):
            val = list(val)
        code_options[k] = val

    instr_gen = InstructionTranslator(frame, code_options)
    instrs = instr_gen.run()
    new_code = gen_new_opcode(instrs, code_options, keys, frame)

    dis.dis(new_code)
    return new_code
