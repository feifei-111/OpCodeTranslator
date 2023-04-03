import paddle
from to_static import to_static

def caller(x):
    y = x + 2 
    ret = paddle.subtract(y, 1)
    print("yes")
    print("no")
    #for i in range(10):
    ret = ret + 2 + x
    return ret

x = paddle.to_tensor([1.0])
to_static(caller)(x)

