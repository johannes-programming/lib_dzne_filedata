import math as _math
import os as _os
import tempfile as _tmp
import tomllib as _tomllib

import lib_dzne_math.na as _na
import tomli_w as _tomli_w


class _File:
    def __init__(self, *, fileDataType, string):
        fileDataType.check_ext(string)
        if not issubclass(fileDataType, FileData):
            raise TypeError()
        if type(string) is not str:
            raise TypeError()
        self._fileDataType = fileDataType
        self._string = string
    @property
    def fileDataType(self):
        return self._fileDataType
    def __str__(self):
        return self._string
    def load(self, /, **kwargs):
        return self._fileDataType.load(file=self._string, **kwargs)
    def save(self, /, data, **kwargs):
        if type(data) is not self._fileDataType:
            raise TypeError()
        return data.save(file=self._string, **kwargs)

class FileData:
    def __init__(self, data):
        if issubclass(type(data), FileData):
            self.data = data._data
        else:
            self.data = data
    def __str__(self):
        with _tmp.TemporaryDirectory() as directory:
            file = _os.path.join(directory, "a"+self.ext())
            txtfile = _os.path.join(directory, "b"+TXTData.ext())
            self.save(file)
            _os.rename(file, txtfile)
            txtdata = TXTData.load(txtfile)
        return str(txtdata)
    @classmethod
    def from_str(cls, string, /):
        txtdata = TXTData.from_str(string)
        with _tmp.TemporaryDirectory() as directory:
            txtfile = _os.path.join(directory, "b"+TXTData.ext())
            file = _os.path.join(directory, "a"+cls.ext())
            txtdata.save(txtfile)
            _os.rename(txtfile, file)
            return cls.load(file)
    @classmethod
    def file(cls, /, string):
        return _File(fileDataType=cls, string=string)
    @classmethod
    def ext(cls):
        return cls._ext
    @classmethod
    def check_ext(cls, /, file):
        if cls._ext == _os.path.splitext(file)[1]:
            return
        raise ValueError(f"{file.__repr__()} has an illegal extension! ")
    @classmethod
    def load(cls, /, file, **kwargs):
        if file == "":
            ans = cls._default()
        else:
            cls.check_ext(file)
            try:
                ans = cls._load(file=file, **kwargs)
            except:
                raise ValueError(f"Loading file {file.__repr__()} failed! ")
        return cls(ans)
    def save(self, /, file, *, overwrite=False, **kwargs):
        cls = type(self)
        if file == "":
            ans = type(self).drop()
        elif _os.path.exists(file) and not overwrite:
            raise FileExistsError(file)
        else:
            cls.check_ext(file)
            ans = self._save(file=file, **kwargs)
        if ans is not None:
            raise TypeError()
    @classmethod
    def from_file(cls, file, /, *types):
        ext = _os.path.splitext(file)[1]
        for t in types:
            if not issubclass(t, cls):
                raise ValueError()
            if t._ext == ext:
                return t.load(file)
        raise ValueError()
    @classmethod
    def default(cls):
        return cls.load("")
    @property
    def data(self):
        return type(self).clone_data(self._data)
    @data.setter
    def data(self, value):
        self._data = type(self).clone_data(value)



class TXTData(FileData):
    _ext = '.txt'
    def __str__(self):
        ans = ""
        for line in self._data:
            ans += line
            ans += '\n'
        return ans
    @classmethod
    def from_str(cls, string, /):
        string = str(string)
        data = string.split('\n')
        ans = cls(data)
        return ans
    @classmethod
    def _load(cls, /, file):
        ans = list()
        with open(file, 'r') as s:
            for line in s:
                if not line.endswith('\n'):
                    raise ValueError()
                ans.append(line[:-1])
        return ans
    def _save(self, /, file):
        with open(file, 'w') as s:
            for line in self._data:
                print(line, file=s)
    @staticmethod
    def _default():
        return list()
    @staticmethod
    def clone_data(data):
        x = list()
        for line in data:
            x += str(line).split('\n')
        return x


class TOMLData(FileData):
    _ext = ".toml"
    def __getitem__(self, key):
        keys = self._getkeys(key)
        ans = self._getitem(*keys)
        ans = self.clone_data(ans)
        return ans
    def __setitem__(self, key, value):
        value = self.clone_data(value)
        keys = self._getkeys(key)
        target = self._getitem(*(keys[:-1]))
        if (type(target) is dict) and (type(keys[-1]) is not str):
            raise TypeError()
        target[keys[-1]] = value
    def __delitem__(self, key):
        keys = self._getkeys(key)
        target = self._getitem(*(keys[:-1]))
        del target[keys[-1]]
    def __add__(self, other):
        if type(self) is not type(other):
            other = type(self)(other)
        return self._add(self, other)
    def __radd__(self, other):
        return self.__add__(other)
    @classmethod
    def _add(cls, *objs):
        ans = cls.default()
        for obj in objs:
            for k, v in obj.iteritems():
                if ans.get(*k) is None:
                    ans[k] = v
                else:
                    raise KeyError()
        return ans
    @staticmethod
    def _getkeys(key):
        if type(key) is tuple:
            return key
        else:
            return key,
    def _getitem(self, *keys):
        target = self._data
        for key in keys:
            target = target[key]
        return target
    def items(self, *keys):
        return self[keys].items()
    def append(self, *args):
        *keys, value = args
        self._getitem(*keys).append(value)
    def get(self, *keys, default=None):
        try:
            return self[keys]
        except KeyError:
            return default
    def iteritems(self):
        return self._iteritems(self.data)
    @classmethod
    def _iteritems(cls, data):
        gen = None
        if type(data) is list:
            gen = enumerate(data)
        elif type(data) is dict:
            gen = data.items()
        else:
            yield (tuple(), data)
            return
        for k, v in gen:
            for keys, value in cls._iteritems(v):
                yield ((k,) + keys), value
    @classmethod
    def clone_data(cls, data):
        if issubclass(type(data), cls):
            data = data._data
        if _na.isna(data):
            return float('nan')
        if type(data) in (str, int, bool, float):
            return data
        if data == str(data):
            return str(data)
        try:
            data = dict(data)
        except:
            pass
        else:
            keys = list(data.keys())
            for k in keys:
                if type(k) is not str:
                    raise TypeError()
                data[k] = cls.clone_data(data[k])
            return data
        try:
            return [cls.clone_data(x) for x in data]
        except:
            pass
        raise TypeError()
    @classmethod
    def _load(cls, /, file):
        with open(file, 'rb') as s:
            return _tomllib.load(s)
    def _save(self, /, file):
        with open(file, 'wb') as s:
            _tomli_w.dump(self.data, s)
    @staticmethod
    def _default():
        return dict()
