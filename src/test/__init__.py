class Test():
    def __init__(self):
        self.attr1 = "attr1"
        self.attr2 = "attr2"

def temp_test():
    t = Test()
    return t.__dict__
    