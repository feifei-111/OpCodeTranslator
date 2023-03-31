import contextlib
import collections
import paddle

from .opcode_transform.transform import transform_opcode


CustomCode = collections.namedtuple("CustomCode", ["code"])


def to_static(func):
    def wrapped(*args, **kw):
        with Dy2staticGuard(eval_frame_callback):
            func(*args, **kw)
    return wrapped


@contextlib.contextmanager
def Dy2staticGuard(callback):
    paddle.fluid.core.set_eval_frame(callback)
    yield
    paddle.fluid.core.set_eval_frame(None)


def eval_frame_callback(frame):
    if frame.f_code.co_name == "caller":
        new_code = transform_opcode(frame)
        retval = CustomCode(new_code)
        return retval
    return None