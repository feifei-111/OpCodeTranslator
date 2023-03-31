import paddle

class ProxyTensor:
    def __init__(self, t):
        assert isinstance(t, paddle.Tensor)
        self.holder = t