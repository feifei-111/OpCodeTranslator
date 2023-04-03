import contextlib
import paddle

from .opcode_transform.transform import eval_frame_callback
from .opcode_transform import convert

def to_static(func, with_log=True):
    convert.LOG_FLAG = with_log
    def wrapped(*args, **kw):
        with Dy2staticGuard(eval_frame_callback):
            func(*args, **kw)
    return wrapped

@contextlib.contextmanager
def Dy2staticGuard(callback):
    with SymbolicTraceContext() as ctx:
        paddle.fluid.core.set_eval_frame(callback)
        yield
        paddle.fluid.core.set_eval_frame(None)
        SymbolicTraceContext().start_compile()
