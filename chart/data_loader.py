from future.utils import lmap, lfilter
import numpy as np
import re
from collections import OrderedDict
from functools import reduce


class DataLoader(object):
    def load(self, data_filename, separator=None):
        raise NotImplementedError

    @property
    def categories(self):
        raise NotImplementedError

    def grouped_data(self, cat):
        raise NotImplementedError
    
    @property
    def X(self):
        raise NotImplementedError


class NormalDataLoader(DataLoader):
    def load(self, data_filename, separator=None):
        f = open(data_filename)
        self.raw_data = [lmap(lambda x: x.strip(), x.strip().split(separator)) for x in filter(len, f)]
        self._categories = self.raw_data[0][1:]
        self._X = [x[0] for x in self.raw_data[1:]]
        self.grouped_Y = {}
        for i in range(0, len(self._categories)):
            cat = self._categories[i]
            self.grouped_Y[cat] = [x[i + 1] for x in self.raw_data[1:]]

    @property
    def category_name(self):
        return self.raw_data[0][0]

    @property
    def categories(self):
        return self._categories

    def grouped_data(self, cat):
        return (self._X, self.grouped_Y[cat])
    
    @property
    def X(self):
        return self._X


class PivotTableDataLoader(DataLoader):
    def load(self, data_filename, separator=None, data_filter=None):
        f = open(data_filename)
        self.raw_data = [lmap(lambda x: x.strip(), x.strip().split(separator)) for x in filter(len, f)]
        self.fields = self.raw_data[0]

        if type(data_filter) is OrderedDict:
            for k in data_filter:
                v = data_filter[k]
                idx = self.fields.index(k)
                new_vec = [self.raw_data[0]]
                for x in self.raw_data[1:]:
                    if re.match(v, x[idx]) != None:
                        new_vec.append(x)
                self.raw_data = new_vec
                # filter(lambda x: x[idx] == v, self.raw_data[1:])
                # print self.raw_data

    def set_fields(self, category_field, independent_variable_field, value_field):
        self.category_field = category_field
        self.indep_var_field = independent_variable_field
        self.value_field = value_field

    def set_default_func(self, func):
        self.default_func = func

    @property
    def categories(self):
        idx = self.fields.index(self.category_field)
        categories = [x[idx] for x in self.raw_data[1:]]
        func = lambda x, y: x if y in x else x + [y]
        ret = reduce(func, [[], ] + categories)
        return sorted(ret)

    def grouped_data(self, cat, func=None):
        idx = self.fields.index(self.value_field)
        cat_idx = self.fields.index(self.category_field)
        x_idx = self.fields.index(self.indep_var_field)
        data = lfilter(lambda x: x[cat_idx] == cat, self.raw_data)
        # print data
        X = self.X
        ret = []

        if not func:
            func = self.default_func

        if func == 'mean':
            func = np.mean
        elif func == 'max':
            func = np.max
        elif func == 'min':
            func = np.min
        elif func == 'median':
            func = np.median
        elif func == 'std':
            func = np.std
        elif func == 'percentile_5':
            func = lambda x: np.percentile(x, 5)
        elif func == 'percentile_95':
            func = lambda x: np.percentile(x, 95)
        else:
            raise Exception("Reduce function not implemented")

        ret_x = []

        for x in X:
            d = lfilter(lambda t: t[x_idx] == x, data)
            if len(d) == 0:
                continue
            ret_x.append(x)
            d = [float(x[idx]) for x in d]
            ret.append(func(d))

        return ret_x, ret

    @property
    def X(self):
        idx = self.fields.index(self.indep_var_field)
        Xs = [x[idx] for x in self.raw_data[1:]]
        func = lambda x, y: x if y in x else x + [y]
        return reduce(func, [[], ] + Xs)
