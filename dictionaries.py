## {{{ http://code.activestate.com/recipes/576642/ (r10)
import pickle, json, csv, os, shutil

class PersistentDict(dict):
    ''' Persistent dictionary with an API compatible with shelve and anydbm.

    The dict is kept in memory, so the dictionary operations run as fast as
    a regular dictionary.

    Write to disk is delayed until close or sync (similar to gdbm's fast mode).

    Input file format is automatically discovered.
    Output file format is selectable between pickle, json, and csv.
    All three serialization formats are backed by fast C implementations.

    '''

    def __init__(self, filename, flag='c', mode=None, format='pickle', *args, **kwds):
        self.flag = flag                    # r=readonly, c=create, or n=new
        self.mode = mode                    # None or an octal triple like 0644
        self.format = format                # 'csv', 'json', or 'pickle'
        self.filename = filename
        if flag != 'n' and os.access(filename, os.R_OK):
            fileobj = open(filename, 'rb' if format=='pickle' else 'r')
            with fileobj:
                self.load(fileobj)
        dict.__init__(self, *args, **kwds)

    def sync(self):
        'Write dict to disk'
        if self.flag == 'r':
            return
        filename = self.filename
        tempname = filename + '.tmp'
        fileobj = open(tempname, 'wb' if self.format=='pickle' else 'w')
        try:
            self.dump(fileobj)
        except Exception:
            os.remove(tempname)
            raise
        finally:
            fileobj.close()
        shutil.move(tempname, self.filename)    # atomic commit
        if self.mode is not None:
            os.chmod(self.filename, self.mode)

    def close(self):
        self.sync()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    def dump(self, fileobj):
        if self.format == 'csv':
            csv.writer(fileobj).writerows(self.items())
        elif self.format == 'json':
            json.dump(self, fileobj, separators=(',', ':'))
        elif self.format == 'pickle':
            pickle.dump(dict(self), fileobj, 2)
        else:
            raise NotImplementedError('Unknown format: ' + repr(self.format))

    def load(self, fileobj):
        # try formats from most restrictive to least restrictive
        for loader in (pickle.load, json.load, csv.reader):
            fileobj.seek(0)
            try:
                return self.update(loader(fileobj))
            except Exception:
                pass
        raise ValueError('File not in a supported format')

## end of http://code.activestate.com/recipes/576642/ }}}

# https://github.com/vkuznet/DotDict
#-*- coding: ISO-8859-1 -*-
"""
File: DotDict.py
Author: Valentin Kuznetsov <vkuznet@gmail.com>

Description:
------------

DotDict is an extension of python dictionary which uses and operates
with dot notations. For example, DotDict.get('a.b.c') or simply
DotDict['a.b.c']. It extends set/get operations to set/assign new
values, as well as provide get_keys/get_values/delete APIs. It also
smart enough to work with complex dict structures. Here is a few
examples:

    .. doctest::

        from ddict import DotDict
        row = {'a':{'b':1, 'c':[1,2]}}
        rec = DotDict(row)
        print rec['a.c']
        [1,2]
        rec['x.y.z'] = 1
        print rec
        {'a':{'b':1, 'c':[1,2]}, 'x': {'y': {'z': 1}}

For a complete list of examples, see DotDict_t.py unit test module.
"""

from types import GeneratorType

def isdictinstance(obj):
    """
    Return if provided object is type of dict or instance of DotDict class
    """
    return isinstance(obj, dict) or isinstance(obj, DotDict)

def convert_dot_notation(key, val):
    """
    Take provided key/value pair and convert it into dict if it
    is required.
    """
    split_list = key.split('.')
    if  len(split_list) == 1: # no dot notation found
        return key, val
    split_list.reverse()
    newval = val
    item = None
    for item in split_list:
        if  item == split_list[-1]:
            return item, newval
        newval = {item:newval}
    return item, newval

def yield_obj(rdict, ckey):
    """
    Helper function for DotDict class. For a given dict and compound key,
    e.g. a.b.c, extract and yield next key and its object(s).
    """
    keys = ckey.split('.')
    key  = keys[0]
    if  len(keys) > 1:
        next_key = '.'.join(keys[1:])
    else:
        next_key = None
    if  rdict.has_key(key):
        obj = rdict[key]
        if  isinstance(obj, list) or isinstance(obj, GeneratorType):
            for item in obj:
                yield next_key, item
        else:
            yield next_key, obj

def helper_loop(combo, vals):
    "Helper function"
    if  isinstance(vals, dict):
        for kkk in DotDict(vals).get_keys():
            yield '%s.%s' % (combo, kkk)
    elif isinstance(vals, list):
        for item in vals:
            if  isinstance(item, dict):
                for kkk in DotDict(item).get_keys():
                    yield '%s.%s' % (combo, kkk)

class DotDict(dict):
    """
    Access python dictionaries via dot notations, original idea taken from
    http://parand.com/say/index.php/2008/10/24/python-dot-notation-dictionary-access/
    Class has been extended with helper method to use compound keys, e.g. a.b.c.
    All extended method follow standard python dictionary syntax.
    """
    def __init__(self, idict):
        super(DotDict, self).__init__(idict)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getattr__(self, key):
        """Overwriten __getattr__ method"""
        obj = super(DotDict, self).get(key, None)
        if  isinstance(obj, dict):
            return DotDict(obj)
        return obj

    def __getitem__(self, key):
        """Overwriten __getitem__ method"""
        return self.get(key)

    def __setitem__(self, key, val):
        """Overwriten __setitem__ method"""
        self._set(key, val)

    def _set(self, ikey, value):
        """
        Set value for provided compound key.
        """
        obj  = self
        keys = ikey.split('.')
        for idx in range(0, len(keys)):
            key = keys[idx]
            if  not obj.has_key(key):
                ckey = '.'.join(keys[idx:])
                nkey, nval = convert_dot_notation(ckey, value)
                if  isinstance(obj, DotDict):
                    super(DotDict, obj).__setitem__(nkey, nval)
                else:
                    obj.__setitem__(nkey, nval)
                return
            if  key != keys[-1]:
                try:
                    obj = super(DotDict, obj).__getitem__(key)
                except:
                    try:
                        obj = obj[key]
                    except:
                        raise
                if  not isinstance(obj, dict):
                    msg = 'Cannot assign new value, internal obj is not dict'
                    raise Exception(msg)
        if  isinstance(obj, DotDict):
            super(DotDict, obj).__setitem__(key, value)
        else:
            obj.__setitem__(key, value)

    def _get_keys(self, ckey):
        """Helper generator which yields all keys for a starting ckey"""
        if  self.has_key(ckey):
            doc = self[ckey]
        else:
            doc = [o for o in self.get_values(ckey)]
        if  isinstance(doc, dict):
            for key in doc.keys():
                if  ckey.rfind('%s.' % key) == -1:
                    combo = '%s.%s' % (ckey, key)
                    yield combo
                    vals = [v for v in self.get_values(combo)]
                    for kkk in helper_loop(combo, vals):
                        yield kkk
                else:
                    yield ckey
        elif isinstance(doc, list):
            for item in doc:
                if  isinstance(item, dict):
                    for key in item.keys():
                        if  ckey.rfind('%s.' % key) == -1:
                            combo = '%s.%s' % (ckey, key)
                            yield combo
                            vals = [v for v in self.get_values(combo)]
                            for kkk in helper_loop(combo, vals):
                                yield kkk
                elif isinstance(item, list):
                    for elem in item:
                        if  isinstance(elem, dict):
                            for kkk in elem.keys():
                                yield '%s.%s' % (ckey, kkk)
                        else:
                            yield ckey
                else: # basic type, so we reach the end
                    yield ckey
        else: # basic type, so we reach the end
            yield ckey

    ### public methods
    def delete(self, ckey):
        """
        Delete provided compound key from DotDict
        """
        obj = self
        keys = ckey.split('.')
        for key in keys:
            if  key == keys[-1]:
                del obj[key]
                break
            if  isinstance(obj, DotDict):
                obj = super(DotDict, obj).__getitem__(key)
            else:
                obj = obj.__getitem__(key)

    def get(self, ckey, default=None):
        """
        Get value for provided compound key. In a case of
        accessed value of a list type returns its first element.
        """
        obj = default
        keys = ckey.split('.')
        first = keys[0]
        if  self.has_key(first):
            obj = super(DotDict, self).__getitem__(first)
            if  first == ckey:
                if  isinstance(obj, dict):
                    return DotDict(obj)
                else:
                    return obj
            if  isdictinstance(obj):
                return DotDict(obj).get('.'.join(keys[1:]))
            elif isinstance(obj, list):
                for elem in obj:
                    if  isdictinstance(elem):
                        newobj = elem.get('.'.join(keys[1:]))
                        if  newobj:
                            if  isinstance(newobj, dict):
                                return DotDict(newobj)
                            return newobj
        return obj

    def get_values(self, ckey):
        """
        Generator which yields values for any compound key. It works
        up to three level deep in DotDict structure.
        """
        for next_key, item in yield_obj(self, ckey):
            if  isdictinstance(item):
                for final, elem in yield_obj(item, next_key):
                    if  isdictinstance(elem) and elem.has_key(final):
                        yield elem[final]
                    else:
                        yield elem
            elif isinstance(item, list) or isinstance(item, GeneratorType):
                for final, elem in item:
                    for last, att in yield_obj(elem, final):
                        if  isdictinstance(att) and att.has_key(last):
                            yield att[last]
                        else:
                            yield att

    def get_keys(self, ckey=None):
        """Return all keys for a starting ckey"""
        if  ckey:
            keys = self._get_keys(ckey)
        else:
            keys = self.keys()
            for key in self.keys():
                keys += [k for k in self._get_keys(key)]
        return list(set(keys))
