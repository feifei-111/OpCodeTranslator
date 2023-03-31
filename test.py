import dis
import paddle
from to_static import to_static

def origin_call():
    print("i am called")


def caller():
    print("caller is calling")
    origin_call()

to_static(caller)()