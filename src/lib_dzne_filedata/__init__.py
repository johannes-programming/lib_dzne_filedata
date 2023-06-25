import math as _math
import os as _os
import tempfile as _tmp
import tomllib as _tomllib

import lib_dzne_math.na as _na
import tomli_w as _tomli_w


class _File:
    def __init__(self, *, fileDataType, string):
        if string is not None:
            fileDataType.check_ext(string)
        if not issubclass(fileDataType, FileData):
            raise TypeError(f"The parameter 'fileDataType' must be the class FileData or one of its subclasses; the value {fileDataType} is illegal! ")
        self._fileDataType = fileDataType
        self._string = string
    @property
    def fileDataType(self):
        return self._fileDataType
    @property
    def ext(self):
        return self._fileDataType.ext()
    def __str__(self):
        if self._string is None:
            raise NotImplementedError("This is an example file; it does not hold an actual path! ")
        return self._string
    def load(self, /, **kwargs):
        return self._fileDataType.load(file=self._string, **kwargs)
    def save(self, /, data, **kwargs):
        if type(data) is not self._fileDataType:
            raise TypeError("The data has the type {type(data)}; the type {self._fileDataType} was expected! ")
        return data.save(file=self._string, **kwargs)

class _Empty:
    """This class only exists to check if a parameter was given. """
    pass

class FileData:
    def __init__(self, data=_Empty):
        if data is _Empty:
            data = self._default()
        if issubclass(type(data), FileData):
            data = data._data
        self.data = data
    def __str__(self):
        with _tmp.TemporaryDirectory() as directory:
            file = _os.path.join(directory, "a"+self.ext())
            txtfile = _os.path.join(directory, "b"+TXTData.ext())
            self.save(file)
            _os.rename(file, txtfile)
            txtdata = TXTData.load(txtfile)
        return str(txtdata)
    def __repr__(self):
        cls = type(self)
        return f"{cls.__name__}({self._data})"
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
    def File(cls, /, string):
        return _File(fileDataType=cls, string=string)
    @classmethod
    def ext(cls):
        return cls._ext
    @classmethod
    def check_ext(cls, /, file):
        if type(file) is not str:
            raise TypeError(f"The file must be represented by a string; {file} of the type {type(file)} was given instead! ")
        if cls._ext == _os.path.splitext(file)[1]:
            return
        raise ValueError(f"{file.__repr__()} has an illegal extension! ")
    @classmethod
    def load(cls, /, file, check_ext=True, **kwargs):
        if file == "":
            return cls()
        if check_ext:
            cls.check_ext(file)
        try:
            ans = cls._load(file=file, **kwargs)
        except:
            raise ValueError(f"Loading file {file.__repr__()} failed! ")
        return cls(ans)
    def save(self, /, file, *, check_ext=True, overwrite=False, **kwargs):
        cls = type(self)
        if file == "":
            ans = type(self).drop()
        elif _os.path.exists(file) and not overwrite:
            raise FileExistsError(f"The file {file.__repr__()} already exists. To allow overwriting please set overwrite=True. ")
        else:
            if check_ext:
                cls.check_ext(file)
            ans = self._save(file=file, **kwargs)
        if ans is not None:
            raise TypeError(f"The function _save must always return None! ")
    @classmethod
    def from_file(cls, file, /, *types):
        ext = _os.path.splitext(file)[1]
        for t in types:
            if not issubclass(t, cls):
                raise ValueError(f"{t} is not a subclass of {cls}! ")
            if t._ext == ext:
                return t.load(file)
        raise ValueError("None of the types fit! ")
    @classmethod
    def default(cls):
        return cls()
    @property
    def data(self):
        return type(self).clone_data(self._data)
    @data.setter
    def data(self, value):
        self._data = type(self).clone_data(value)



class TXTData(FileData):
    # this class is mostly just like a list of strings


    # every type of filedata needs an extension
    _ext = '.txt'



    # The dunder methods are meant to make TXTData like list. ""
    def __add__(self, other):
        return self._add(self, other)
    def __radd__(self, other):
        return self._add(other, self)
    def __mul__(self, other):
        return self._mul(other)
    def __rmul__(self, other):
        return self._mul(other)
    def __str__(self):
        ans = ""
        for line in self._data:
            ans += line
            ans += '\n'
        return ans
    def __len__(self):
        return len(self._data)
    def __iter__(self):
        for line in self._data:
            yield line
    def __getitem__(self, index):
        return self._data[index]
    def __setitem__(self, index, value):
        if type(index) is int:
            value, = self.clone_data([value])
            self._data[index] = value
        elif type(index) is slice:
            lines = self.clone_data(value)
            self._data[index] = lines
        else:
            raise TypeError(f"{type(self).__name__} accepts an index only of the type slice or int. ")
    def __delitem__(self, index):
        del self._data[index]
        

    #   these functions help with mathematical operations
    @classmethod
    def _add(cls, *objs):
        data = list()
        for obj in objs:
            data += cls(obj)._data
        return cls(data)
    def _mul(self, n):
        cls = type(self)
        data = self._data
        data *= n
        ans = cls(data)
        return data

    #   methods to make this class more like list
    def append(self, line, /):
        line, = self.clone_data([line])
        self._data.append(line)
    def pop(self, *args, **kwargs):
        return self._data.pop(*args, **kwargs)


    #   only TXTData overwrites from_str to avoid circlurity
    @classmethod
    def from_str(cls, string, /):
        string = str(string)
        data = string.split('\n')
        ans = cls(data)
        return ans

    #   these methods overwrite what needs to be overwritten
    @classmethod
    def _load(cls, /, file):
        ans = list()
        with open(file, 'r') as s:
            for line in s:
                if not line.endswith('\n'):
                    raise ValueError(f"The file {file.__repr__()} is not formatted as expected by {cls}! ")
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
        ans = self.clone_data(ans, toplevel=False)
        return ans
    def __setitem__(self, key, value):
        value = self.clone_data(value)
        keys = self._getkeys(key)
        target = self._getitem(*(keys[:-1]))
        if (type(target) is dict) and (type(keys[-1]) is not str):
            raise TypeError(f"{keys[-1]} is of the type {type(keys[-1])}, but only a string is legal. ")
        target[keys[-1]] = value
    def __delitem__(self, key):
        keys = self._getkeys(key)
        target = self._getitem(*(keys[:-1]))
        del target[keys[-1]]
    def __add__(self, other):
        return self._add(self, other)
    def __radd__(self, other):
        return self._add(other, self)
    @classmethod
    def _add(cls, *objs):
        ans = cls.default()
        for obj in objs:
            for k, v in cls(obj).iteritems():
                if ans.get(*k) is None:
                    ans[k] = v
                else:
                    raise KeyError()
        return cls(ans)
    @staticmethod
    def _getkeys(key):
        if type(key) is tuple:
            return key
        else:
            return (key,)
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
    def clone_data(cls, data, *, toplevel=True):
        if toplevel:
            data = dict(data)
            cls._clone_dict_items(data)
            return data
        else:
            return cls._clone_value(data)
    @classmethod
    def _clone_value(cls, data):
        if issubclass(type(data), cls):
            data = dict(data.data)
            cls._clone_dict_items(data)
            return data
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
            cls._clone_dict_items(data)
            return data
        try:
            data = list(data)
        except:
            pass
        else:
            cls._clone_list_items(data)
            return data
        raise TypeError()
    @classmethod
    def _clone_dict_items(cls, data):
        keys = list(data.keys())
        for k in keys:
            cls._check_key(k)
            data[k] = cls.clone_data(data[k], toplevel=False)
    @classmethod
    def _check_key(cls, key):
        if type(key) is not str:
            raise TypeError()
    @classmethod
    def _clone_list_items(cls, data):
        for i in range(len(data)):
            data[i] = cls.clone_data(data[i], toplevel=False)
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

def is_File(value, /):
    if value is _File:
        return True
    try:
        fileObj = value(None)
    except Exception as err:
        return False
    cls = type(fileObj)
    return cls is _File

