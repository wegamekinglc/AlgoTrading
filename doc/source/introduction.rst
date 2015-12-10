.. _introduction:

介绍
-----------------

组件
^^^^^^^^^^^^^^^^^

1. *DataAPI*

  提供部门内部数据的访问能力，如果开发基于部门数据库(datacenter)的策略需要该模块。

2. *Finance-Python*

  主要提供与金融数据相关的计算功能。

3. *AlgoTrading*

  基于事件循环的回测引擎。

4. *VisualPortfoilo*

  策略回测结果的可视化展现。可以单独使用。

以上所有的项目都可以在 svn 中找到，并且 直接通过项目根目录的下的 ``setup.py`` 文件安装::

	python setup.py install
	
流程
^^^^^^^^^^^^^^^^^

下面的图展示了，各个模块在运行时的互相作用关系：

.. figure:: ../_static/process.png

	策略运行回测流程图
	
如何开始一个策略
^^^^^^^^^^^^^^^^^^

定义策略
""""""""""""""""""

用户自定义的策略继承自基类 ``Strategy``, 其中用户需要自定义的包括两部分：

* ``__init__``

  初始化函数，在策略启动的时候运行，主要用于定义比如：

  1. 全局变量
  2. 指标（由Finance-Python模块提供）
    
* ``handle_data``

  行情数据处理函数，每根bar推送至回测引擎时候出发。这里是用户交易逻辑的主要定义点。

.. code-block:: python

	class UserStrategy(strategy):
	
		def __init__(self):
			...
		
		def handle_data(self):
			...

运行策略
""""""""""""""""""

当策略就绪之后，直接使用 ``strategyRunner`` 进行回测：

.. code-block:: python

	strategyRunner(strategy=UserStrategy, ...)
	
在 ``strategyRunner`` 中需要补充下面几个必填参数：

1. ``symbolList``

  用户关注的行情数据代码，是一个字符串类型的数组（现阶段可以包括，股票、期货以及指数）
    
2. ``startDate``

  回测周期开始时间，是 ``python`` 的 ``datetiem`` 类型对象。
    
3. ``endDate``

  回测周期结束时间，是 ``python`` 的 ``datetiem`` 类型对象。

4. ``dataSource``

  数据源，默认值为：``DataSource.DXDataCenter``，意味着使用部门的 ``datacenter`` 数据库。
    
一个典型的  ``strategyRunner`` 调用如下形式：

.. code-block:: python

	strategyRunner(strategy=UserStrategy, \
	               symbolList=['600000.xshg', '000300.zicn', 'if1512'], \
	               startDate=dt.datetime(2012, 1, 1), \
	               endDate=dt.datetiem(2015, 11, 19))
