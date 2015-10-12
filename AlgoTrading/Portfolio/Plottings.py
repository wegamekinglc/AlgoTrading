# -*- coding: utf-8 -*-
u"""
Created on 2015-10-9

@author: cheng.li
"""

from functools import wraps
import seaborn as sns
import matplotlib
from matplotlib.ticker import FuncFormatter
import pandas as pd
from AlgoTrading.Finance.Timeseries import aggregateReturns


def plotting_context(func):
    @wraps(func)
    def call_w_context(*args, **kwargs):
        set_context = kwargs.pop('set_context', True)
        if set_context:
            with context():
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return call_w_context


def context(context='notebook', font_scale=1.5, rc=None):
    if rc is None:
        rc = {}

    rc_default = {'lines.linewidth': 1.5,
                  'axes.facecolor': '0.995',
                  'figure.facecolor': '0.97'}

    # Add defaults if they do not exist
    for name, val in rc_default.items():
        rc.setdefault(name, val)

    return sns.plotting_context(context=context, font_scale=font_scale,
                                rc=rc)


def one_dec_places(x, pos):
    return '%.1f' % x


def percentage(x, pos):
    return '%.0f%%' % (x * 100)


def plottingRollingReturn(cumReturns, ax):

    y_axis_formatter = FuncFormatter(one_dec_places)
    ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))

    cumReturns.plot(lw=3,
                    color='forestgreen',
                    alpha=0.6,
                    label='Cumulative returns',
                    ax=ax)

    ax.axhline(0.0, linestyle='--', color='black', lw=2)
    ax.set_ylabel('Cumulative returns')
    ax.set_title('Cumulative Returns')
    ax.legend(loc='best')
    return ax


def plottingDrawdownPeriods(cumReturns, drawDownTable, top, ax):
    y_axis_formatter = FuncFormatter(one_dec_places)
    ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))
    cumReturns.plot(ax=ax)
    lim = ax.get_ylim()

    tmp = drawDownTable.sort('draw_down')
    topDrawdown = tmp.groupby('recovery').first()
    topDrawdown = topDrawdown.sort('draw_down')[:top]
    colors = sns.cubehelix_palette(len(topDrawdown))[::-1]
    for i in range(len(colors)):
        recovery = topDrawdown.index[i]
        ax.fill_between((topDrawdown['peak'][i], recovery),
                        lim[0],
                        lim[1],
                        alpha=.4,
                        color=colors[i])

    ax.set_title('Top %i Drawdown Periods' % top)
    ax.set_ylabel('Cumulative returns')
    ax.legend(['Cumulative returns'], loc='best')
    ax.set_xlabel('')
    return ax


def plottingUnderwater(drawDownSeries, ax):
    y_axis_formatter = FuncFormatter(percentage)
    ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))
    drawDownSeries.plot(ax=ax, kind='area', color='coral', alpha=0.7)
    ax.set_ylabel('Drawdown')
    ax.set_title('Underwater Plot')
    ax.legend(loc='best')
    ax.set_xlabel('')
    return ax


def plottingMonthlyReturnsHeapmap(returns, ax):
    monthlyRetTable = aggregateReturns(returns, 'monthly')
    monthlyRetTable = monthlyRetTable.unstack()
    sns.heatmap(monthlyRetTable.fillna(0) * 100.0,
                annot=True,
                annot_kws={"size": 9},
                alpha=1.0,
                center=0.0,
                cbar=False,
                cmap=matplotlib.cm.RdYlGn,
                ax=ax)
    ax.set_ylabel('Year')
    ax.set_xlabel('Month')
    ax.set_title('Monthly Returns (%)')
    return ax


def plottingAnnualReturns(returns, ax):
    x_axis_formatter = FuncFormatter(percentage)
    ax.xaxis.set_major_formatter(FuncFormatter(x_axis_formatter))
    ax.tick_params(axis='x', which='major', labelsize=10)

    annulaReturns = pd.DataFrame(aggregateReturns(returns, 'yearly'))

    ax.axvline(annulaReturns.values.mean(),
               color='steelblue',
               linestyle='--',
               lw=4,
               alpha=0.7)

    annulaReturns.sort_index(ascending=False).plot(
        ax=ax,
        kind='barh',
        alpha=0.7
    )

    ax.axvline(0.0, color='black', linestyle='-', lw=3)

    ax.set_ylabel('Year')
    ax.set_xlabel('Returns')
    ax.set_title("Annual Returns")
    ax.legend(['mean'], loc='best')
    return ax


def plottingMonthlyRetDist(returns, ax):
    x_axis_formatter = FuncFormatter(percentage)
    ax.xaxis.set_major_formatter(FuncFormatter(x_axis_formatter))
    ax.tick_params(axis='x', which='major', labelsize=10)

    monthlyRetTable = aggregateReturns(returns, 'monthly')

    ax.hist(
        monthlyRetTable,
        color='orangered',
        alpha=0.8,
        bins=20
    )

    ax.axvline(
        monthlyRetTable.mean(),
        color='gold',
        linestyle='--',
        lw=4,
        alpha=1.0
    )

    ax.axvline(0.0, color='black', linestyle='-', lw=3, alpha=0.75)
    ax.legend(['mean'], loc='best')
    ax.set_ylabel('Number of months')
    ax.set_xlabel('Returns')
    ax.set_title("Distribution of Monthly Returns")
    return ax