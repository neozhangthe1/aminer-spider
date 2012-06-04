from bs4 import UnicodeDammit

def ClassListUnicode(fn):
    def wrap(self, p):
        l = fn(self, p)
        return [UnicodeDammit(x).unicode_markup 
                if x is not None 
                else None
                for x in l]
    return wrap

def ClassUnicode(fn):
    def wrap(self, p):
        s = fn(self, p)
        return UnicodeDammit(s).unicode_markup
    return wrap

def ClassBeforeUnicode(fn):
    def wrap(self, p):
        p = UnicodeDammit(p).unicode_markup
        return fn(self, p)
    return wrap

if __name__ == '__main__':
    print test('a')