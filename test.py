import dis
import paddle
from to_static import to_static

def origin_call():
    print("i am called")
    return 1,2,3


def caller():
    print("caller is calling")
    a,b,c = origin_call()
    print(a,b,c)

to_static(caller)()