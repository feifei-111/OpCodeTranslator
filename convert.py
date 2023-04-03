import paddle
from ProxyTensor import ProxyTensor, paddle_api_wrapper
from symbolic_trace import SymbolicTraceContext

def convert_one(obj):
    print(f"convert: {obj}")
    if callable(obj):
        return dy2static_call(obj)
    if isinstance(obj, paddle.Tensor):
        print("found a tensor")
        return convert_tensor(obj)
    print("nothing happend")
    return obj


def convert_multi(args):
    retval = []
    for obj in args:
        retval.append(convert_one(obj))
    return tuple(retval)
  
def dy2static_call(func):
    return paddle_api_wrapper(func)

def convert_tensor(tensor):
    return ProxyTensor.from_tensor(tensor)
