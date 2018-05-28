#coding=utf-8
from __future__ import print_function
from future.utils import lmap, lfilter
import matplotlib
matplotlib.use('Agg') # reset matplotlib

from chart.data_loader import NormalDataLoader, PivotTableDataLoader
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter, ScalarFormatter, NullFormatter, FixedLocator
from functools import reduce
import json
import os
import numpy as np
import re
from collections import OrderedDict

colors = [
    ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#75755c", "#a65628", "#f781bf",],
    ["#8dd3c7", "#bebada", "#fb8072", "#80b1d3", "#fdb462", "#b3de69", "#fccde5",]
]

bar_patterns = ('//', 'xxx', '\\\\', '*', 'o', 'O', '.')

class DrawingCore:

    def __init__(self, filename, settings, mode):
        print("%s " % filename, end="")
        self.filename = filename
        self.mode = mode
        self.x_points = []
        self.y_points_arr = []
        self.x_label = None
        self.y_label = None
        self.categories = []
        self.legends = []
        self.colors = colors[0]
        self.bar_colors = self.colors
        self.point_types = ['s-', '^-', 'o-', '*-', 'H-', 'd-', 'h-', '<-', '2-', 'v-']

        self.output_file = self.filename.split('.')[0] + '.pdf'
        if 'output' in settings:
            self.output_file = settings['output']

        self.draw_data = []
        self.draw_data_output_file = ".".join(self.output_file.split('.')[0:-1]) + '.txt'

        self.settings = {
            'x_label': None,
            'y_label': None,
            'chart.type': 'line',
            'errorBar': False,
            'pivotTable': False,
            'pivotTable.point': 'median',
            'pivotTable.errorBar': 'min-max',
            'style': 4,
            'marker': True,
            'separator': None,
            'legend.loc': 'best',
            'legend.ncol': '1',
            'legend.mode': None,
            'legend.bbox_to_anchor': None,
            'legend.handlelength': None,

            'data.n_groups': None,

            'xtick.log': False,
            'ytick.log': False,

            'xtick.force_non_digit': False,
            'xtick.order': False,

            'grid.horizontal': None,
            'grid.vertical': None,

            'categories': False,

            'filter': False
        }
        self.settings.update(settings)
        self.x_label = self.settings['x_label']
        self.y_label = self.settings['y_label']
        self.rcParams = {}
        if 'rcParams' in settings:
            self.rcParams = settings['rcParams']

        self.init_plt()
        self.init_data()

        self.draw()

    def init_plt(self):
        f = open(os.path.split(os.path.realpath(__file__))[0] + '/rcParams_' + str(self.settings['style']) + '.json')
        input_str = "\n".join(f.readlines())
        input_str = re.sub(r'\\\n', '', input_str)
        input_str = re.sub(r'//.*\n', '\n', input_str)
        params = json.loads(input_str, object_pairs_hook=OrderedDict)
        if self.mode == "draft":
            params.update({'text.usetex': False})
        plt.rcParams.update(params)
        plt.clf()
        f.close()

    def init_data(self):
        if self.settings['pivotTable']:
            self.data = PivotTableDataLoader()
            self.data.load(self.filename, self.settings['separator'], data_filter=self.settings['filter'])
            self.data.set_fields(self.settings['pivotTable.category'], self.settings['pivotTable.independentVariable'], self.settings['pivotTable.value'])
            self.data.set_default_func(self.settings['pivotTable.point'])
            if not self.x_label:
                self.x_label = self.settings['pivotTable.independentVariable']
            if not self.y_label:
                self.y_label = self.settings['pivotTable.value']
        else:
            self.data = NormalDataLoader()
            self.data.load(self.filename, self.settings['separator'])
            if not self.x_label:
                self.x_label = self.data.category_name

    def draw(self):
        plt.grid(True, linestyle='--')
        ax = plt.gca()
        if not self.settings['grid.vertical']:
            ax.xaxis.grid(False)
        if not self.settings['grid.horizontal']:
            ax.yaxis.grid(False)
        # ax.spines['right'].set_color('none')
        # ax.spines['top'].set_color('none')

        if self.settings['pivotTable'] and self.settings['pivotTable.errorBar']:
            self.settings['errorBar'] = True
        if self.settings['chart.type'] == 'line':
            self.draw_line()
        elif self.settings['chart.type'] == 'bar':
            self.draw_bar()

        if 'xtick.lim' in self.settings:
            plt.xlim(self.settings['xtick.lim'])
        if 'ytick.lim' in self.settings:
            plt.ylim(self.settings['ytick.lim'])
        if 'xtick.interval' in self.settings:
            start, end = ax.get_xlim()
            ax.xaxis.set_ticks(np.arange(start, end + self.settings['xtick.interval'], self.settings['xtick.interval']))
        if 'xtick.nbins' in self.settings:
            ax.locator_params(axis='x', nbins=self.settings['xtick.nbins'])
        if 'ytick.interval' in self.settings:
            start, end = ax.get_ylim()
            ax.yaxis.set_ticks(np.arange(start, end + self.settings['ytick.interval'], self.settings['ytick.interval']))
        if 'ytick.nbins' in self.settings:
            ax.locator_params(axis='y', nbins=self.settings['ytick.nbins'])
        if 'xtick.use_k' in self.settings:
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x, y: str(int(x / 1000)) + 'k'))

        scalar_formatter = ScalarFormatter()
        scalar_formatter.set_scientific(False)
        scalar_formatter.labelOnBase = False
        null_formatter = NullFormatter()
        null_formatter.labelOnBase = False

        if self.settings['xtick.log']:
            ax.set_xscale('log')
            if self.settings['xtick.log'] != True:
                ax.set_xscale('log', basex=self.settings['xtick.log'])
            ax.xaxis.set_major_formatter(scalar_formatter)
            ax.xaxis.set_minor_formatter(null_formatter)
        if self.settings['ytick.log']:
            ax.set_yscale('log')
            if self.settings['ytick.log'] != True:
                ax.set_yscale(self.settings['ytick.log'])
            ax.yaxis.set_major_formatter(scalar_formatter)
            ax.yaxis.set_minor_formatter(null_formatter)

        if 'xticks' in self.settings:
            ax.xaxis.set_ticks(self.settings['xticks'], lmap(str, self.settings['xticks']))
            fixed_locator = FixedLocator(self.settings['xticks'])
            ax.xaxis.set_major_locator(fixed_locator)

        if 'yticks' in self.settings:
            ax.yaxis.set_ticks(self.settings['yticks'], lmap(str, self.settings['yticks']))
            fixed_locator = FixedLocator(self.settings['yticks'])
            ax.yaxis.set_major_locator(fixed_locator)

        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)

        plt.legend(loc=self.settings['legend.loc'], ncol=int(self.settings['legend.ncol']),
                   mode=self.settings['legend.mode'], bbox_to_anchor=self.settings['legend.bbox_to_anchor'],
                   handlelength=self.settings['legend.handlelength'],
                   borderpad=0.3)


        plt.savefig(self.output_file)
        plt.close()

        if self.settings['errorBar']:
            self.output_draw_data()

        print('done.')

    def draw_line(self):
        x_points = self.data.X
        if self.settings['xtick.order']:
            x_points = self.settings['xtick.order']
        is_digit = reduce(lambda x, y: x and not re.match(r'[+-]?\d+(.\d+)?$', y) == None, x_points, True)
        if self.settings['xtick.force_non_digit']:
            is_digit = False
        map_dict = {}
        if not is_digit:
            x_ticks = x_points
            x_points = range(0, len(x_points))
            plt.xticks(range(0, len(x_points)), x_ticks)
            plt.xlim((-1, len(x_points)))
            for i in range(0, len(x_points)):
                map_dict[x_ticks[i]] = i

        for i in range(0, len(self.data.categories)):
            points_type = self.point_types[i]
            if self.settings['categories']:
                if i >= len(self.settings['categories']):
                    break
                if type(self.settings['categories']) == list:
                    cat = self.settings['categories'][i]
                    cat_name = cat
                elif type(self.settings['categories']) == OrderedDict:
                    cat = list(self.settings['categories'])[i]
                    cat_name = self.settings['categories'][cat]
            else:
                cat = self.data.categories[i]
                cat_name = cat
            points = self.data.grouped_data(cat)
            if not self.settings['marker']:
                points_type = points_type[1:2]

            y_points = points[1]
            new_xp = points[0]
            if is_digit:
                x_points = [float(x) for x in points[0]]
            else:
                if self.settings['xtick.order']:
                    new_xp = []
                    y_points = []
                    for x in self.settings['xtick.order']:
                        if x in points[0]:
                            new_xp.append(x)
                            y_points.append(points[1][points[0].index(x)])
                x_points = [map_dict[x] for x in new_xp]
            if i >= len(self.colors):
                print("too many lines")

            # transform y points to float
            y_points = lmap(float, y_points)
            plt.plot(x_points, y_points, points_type, color=self.colors[i], label=cat_name, alpha=1)
            if self.settings['errorBar']:
                points_err = self.get_error_data(cat, new_xp)
                # print points_err
                plt.errorbar(x_points, y_points, yerr=points_err, ecolor=self.colors[i],
                             color=self.colors[i], alpha=1, fmt="none", elinewidth=3, capsize=5)

    def get_error_data(self, cat, x_points):
        points = self.data.grouped_data(cat)
        f_data = [points[0], points[1]]

        if self.settings['pivotTable.errorBar'] == 'min-max':
            points_up = np.array(self.data.grouped_data(cat, 'max')[1])
            points_down = np.array(self.data.grouped_data(cat, 'min')[1])
            f_data.append(points_down)
            f_data.append(points_up)
            points_err = [np.array(points[1]) - points_down, points_up - np.array(points[1])]
        elif self.settings['pivotTable.errorBar'] == 'percentile':
            points_up = np.array(self.data.grouped_data(cat, 'percentile_95')[1])
            points_down = np.array(self.data.grouped_data(cat, 'percentile_5')[1])
            f_data.append(points_down)
            f_data.append(points_up)
            points_err = [np.array(points[1]) - points_down, points_up - np.array(points[1])]
        elif self.settings['pivotTable.errorBar'] == 'std':
            points_delta = np.array(self.data.grouped_data(cat, 'std')[1])
            f_data.append(points_delta)
            points_err = [points_delta, points_delta]
        else:
            raise Exception("Error bar function not implemented")

        ret_err = [[],[]]
        # print points[0].index(u'4')
        # print x_points
        for x in x_points:
            idx = points[0].index(x)
            ret_err[0].append(points_err[0][idx])
            ret_err[1].append(points_err[1][idx])

        self.draw_data.append((cat, f_data))

        return ret_err

    def draw_bar(self):
        tot_width = 0.8
        x_points_origin = (self.data.X)
        if self.settings['xtick.order']:
            x_points_origin = self.settings['xtick.order']

        map_dict = {}
        x_ticks = x_points_origin
        for i in range(0, len(x_points_origin)):
            map_dict[x_ticks[i]] = i

        xs = range(0, len(x_points_origin))
        categories = self.data.categories
        if self.settings['categories']:
            categories = self.settings['categories']
        width = tot_width / len(categories)
        # print width
        for i in range(0, len(categories)):
            if self.settings['categories']:
                if i >= len(self.settings['categories']):
                    break
                if type(self.settings['categories']) == list:
                    cat = self.settings['categories'][i]
                    cat_name = cat
                elif type(self.settings['categories']) == OrderedDict:
                    cat = self.settings['categories'].keys()[i]
                    cat_name = self.settings['categories'][cat]
            else:
                cat = self.data.categories[i]
                cat_name = cat
            points = self.data.grouped_data(cat)

            y_points = points[1]
            x_points = xs
            new_xp = points[0]
            if self.settings['xtick.order']:
                new_xp = []
                y_points = []
                for x in self.settings['xtick.order']:
                    if x in points[0]:
                        new_xp.append(x)
                        y_points.append(points[1][points[0].index(x)])
                x_points = map(lambda xx: map_dict[xx], new_xp)

            # print map(lambda x: x - tot_width / 2 + i * width, xs)
            if not self.settings['errorBar']:
                bars = plt.bar(lmap(lambda x: x - tot_width / 2 + i * width + width / 2, x_points), lmap(lambda x: float(x), y_points),
                        width, color=self.bar_colors[i], label=cat_name,
                        )
            else:
                points_err = self.get_error_data(cat, new_xp)
                bars = plt.bar(lmap(lambda x: x - tot_width / 2 + i * width + width / 2, x_points), lmap(lambda x: float(x), y_points),
                        width,
                        color=self.bar_colors[i],
                        label=cat_name, yerr=points_err, capsize=3,
                        # hatch=bar_patterns[i],
                        edgecolor=[self.bar_colors[i]] * len(x_points) # hack for matplotlib 2.1.0
                        )
            # for bar in bars:
            #     bar.set_hatch(bar_patterns[i])
        plt.xlim(-0.7, len(xs) - 0.3)
        plt.xticks(lmap(lambda x: x, range(0, len(x_points_origin))), x_points_origin)

    def output_draw_data(self):
        f = open(self.draw_data_output_file, "w")

        for d in self.draw_data:
            f.write("%s\n" % d[0])

            header = "%10s" % "x"
            header += "%10s" % self.settings['pivotTable.point']
            if self.settings['pivotTable.errorBar'] == 'min-max':
                header += "%10s%10s" % ("y-min", "y-max")
            elif self.settings['pivotTable.errorBar'] == 'percentile':
                header += "%10s%10s" % ("y-5th", "y-10th")
            elif self.settings['pivotTable.errorBar'] == 'std':
                header += "%10s" % "y-std-dev"

            f.write(header + "\n")
            f.write("=" * 40 + "\n")

            def isNum(value):
                try:
                    value + 1
                except TypeError:
                    return False
                else:
                    return True

            for i in range(0, len(d[1][0])):
                for j in range(0, len(d[1])):
                    o = d[1][j][i]
                    if isNum(o):
                        o = "%.6lf" % d[1][j][i]
                    f.write("%10s" % o)
                f.write("\n")

            f.write("\n")
            f.write("-" * 50 + "\n\n\n\n")

        f.close()
