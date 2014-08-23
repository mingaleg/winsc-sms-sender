import pickle

class FileDictException(Exception):
    pass

class FileDict:
    def __init__(self, filename, encoding = 'cp1251'):
        self.own = {}
        self.filename = filename
        self.encoding = encoding
        try:
            self.own = pickle.load(open(filename, 'rb'), encoding=encoding)
        except:
            pass
    def __getitem__(self, ind):
        if ind not in self.own:
            raise FileDictException("No such index: " + ind)
        return self.own[ind]
    def __delitem__(self, ind):
        if ind not in self.own:
            raise FileDictException("No such index: " + ind)
        del self.own[ind]
        pickle.dump(self.own, open(self.filename, 'wb'))
    def __setitem__(self, ind, val):
        self.own[ind] = val
        pickle.dump(self.own, open(self.filename, 'wb'))
    def __contains__(self, ind):
        return ind in self.own
    def __repr__(self):
        return self.own.__repr__()
    def __str__(self):
        return self.own.__str__()
    def __iter__(self):
        return self.own.__iter__()
    def reload(self):
        try:
            self.own = pickle.load(open(filename, 'rb'), encoding=encoding)
        except:
            self.own = {}
    def keys(self):
        return self.own.keys()

class FileLimitedList:
    def __init__(self, limit, filename, encoding = 'cp1251'):
        self.own = []
        self.filename = filename
        self.encoding = encoding
        self.limit = limit
        try:
            self.own = pickle.load(open(filename, 'rb'), encoding=encoding)
        except:
            pass
    def normalize(self):
        if len(self.own) > self.limit:
            self.own = self.own[len(self.own) - self.limit:]
        pickle.dump(self.own, open(self.filename, 'wb'))
    def __getitem__(self, ind):
        return self.own[ind]
    def __delitem__(self, ind):
        del self.own[ind]
        pickle.dump(self.own, open(self.filename, 'wb'))
    def __setitem__(self, ind, val):
        self.own[ind] = val
        pickle.dump(self.own, open(self.filename, 'wb'))
    def __contains__(self, ind):
        return ind in self.own
    def __repr__(self):
        return self.own.__repr__()
    def __str__(self):
        return self.own.__str__()
    def __iter__(self):
        return self.own.__iter__()
    def append(self, val):
        self.own.append(val)
        self.normalize()
    def reload(self):
        try:
            self.own = pickle.load(open(filename, 'rb'), encoding=encoding)
        except:
            self.own = []
