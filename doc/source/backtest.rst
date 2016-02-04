.. _backtest_doc:

回测
-----------------

.. index:: 回测

现在最常用的回测工具为 ``strategyRunner`` ，可以从 ``api`` 模块中导入：

.. code:: python

    from AlgoTrading.api import api

如何使用
^^^^^^^^^^^^^^^^

参数设置
""""""""""""""""

``strategyRunner`` 通过输入一组配置参数来运行某个自定义策略

* ``userStrategy``

用户的自定义策略，这个参数必须是继承自基类 ``strategy`` 。可以是一个类类型或者是一个类实例。必填。

* ``strategyParameters``

用户自定义策略的参数设置，例如，用户有如下的自定义策略的初始化函数：

.. code:: python

    class UserStrategy(Strategy):
    
        def __init__(self, param1, param2):
            ...
            
        ...
        
那么如果用户设置： ``strategyParameters=(5,10)`` ，那么传入 ``__init__`` 的参数即为： ``param1=5, param2=10`` 。

这个参数为选填，默认为空。

* ``initialCapital``

初始资金设置，默认为100000元。

* ``symbolList``

初始证券列表，默认为：600000.xshg。

* ``startDate``

回测开始日期，默认为：2015年9月1日。

* ``endDate``

回测结束日期，默认为：2015年9月15日。

* ``dataSource``

回测使用数据源，默认为：``DXDataCenter`` ，即为使用东兴量化自研数据库。

* ``benchmark``

用来比较的基准，现阶段支持输入任意股票指数，默认为None，不与任何基准做比较。

* ``refreshRate``

定义 ``userStrategy`` 中 ``handle_data`` 的刷新周期，例如：值为30，则每30根bar线调用一次 ``handle_data`` 。
默认为1，每根bar线上都调用 ``handle_data`` 。

* ``saveFile``

是否保存数据为本地csv文件。若为True，则策略回测完成后，会把所有表现的数据保存至当前目录下performance文件夹。默认为False。

* ``plot``

是否绘制策略回撤表现图表。若为True，则会直接绘图。默认为False。

* ``logLevel``

记录日志的等级，只记录 ``logLevel`` 所定义的日志级别更高的信息。默认为info。日志会保存在当前目录strategy.log文件中。

* ``portfolioType``

使用的计算策略收益的方式，有两种选择：

    * FullNotional ：没有现金的概念，策略收益即为信号本身的收益。选择这种方式时， ``initialCapital`` 选项无效。
    
    * CashManageable ：从初始资金出发，整体收益来自与证券头寸的收益以及现金留存。
    
默认为FullNotional。

* ``**kwargs``

其他的一些关键字参数，例如：在设置 ``dataSource=DataSource.DXDataCenter`` 时，需要设置 ``freq`` 参数来控制使用bar线的类型（1分钟，5分钟或者日线）。

输出信息
""""""""""""""""

``strategyRunner`` 返回的是一个包含各种回测信息的python字典，包含的内容有：

    * perf_metric：回测表现，主要包含收益，以及波动率等。
    
    * perf_series：回测的每日表现，例如收益，回撤。
    
    * equity_curve：净值曲线。包括分品种的每日价值。
    
    * order_book：历史下单情况。
    
    * filled_book：历史成交记录。
    
    * transactions：成交量以及成交额。
    
    * turnover_rate：换手情况。
    
    * user_info：用户自定义记录的信息。

.. ipython::
    
    @suppress
    In [1]: %run scripts/savePerfData
    
    @suppress
    In [2]: import pickle
       ...: with open('data/data.dat', 'rb') as f:
       ...:     perf_data = pickle.load(f)

.. code:: python

    perf_data = strategyRunner(...)
    
.. ipython::

    In [1]: perf_data['perf_metric']
    
.. ipython::

    In [2]: perf_data['perf_series'].tail()
    
.. ipython::

    In [3]: perf_data['equity_curve'].tail()
    
.. ipython::

    In [4]: perf_data['order_book'].head()
    
.. ipython::

    In [5]: perf_data['filled_book'].head()
    
.. ipython::

    In [6]: perf_data['transactions'].head()
    
.. ipython::

    In [7]: perf_data['user_info'].tail()

回测模块
^^^^^^^^^^^^^^^^

.. autofunction:: AlgoTrading.api.strategyRunner