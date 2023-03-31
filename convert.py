import paddle
from ProxyTensor import ProxyTensor


def convert_one(obj):
    print(f"convert: {obj}")
    if callable(obj):
        print("found a callable object")
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
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def convert_tensor(tensor):
    return ProxyTensor(tensor)