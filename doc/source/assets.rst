.. _assets:

资产类型
------------------

.. index:: 资产类型

资产类型模块中定义了现在回测框架下支持的品种:

* ``XSHGStock`` ：上海证券交易所股票
* ``XSHEStock`` ：深圳证券交易所股票
* ``IFFutures`` ：中国金融期货交易所沪深300指数期货
* ``IHFutures`` ：中国金融期货交易所上证50指数期货
* ``ICFutures`` ：中国金融期货交易所中证500指数期货
* ``EXIndex`` ：证券交易所指数

资产属性
^^^^^^^^^^^^^^^^^^

.. index:: 资产属性

1. ``commission``

资产的手续费设置。

2. ``exchange``

所属交易所。

3. ``lag``

T+x设置。例如：``lag=0``，意味着该品种支持T+0交易。

4. ``margin``

保证金设置。现阶段该参数未被启用。

5. ``minimum``

最小交易单位。

6. ``multiplier``

品种价格乘数。

7. ``settle``

交易现金使用比例，例如：股票类资产比例为1（即为100%），期货类为0。

8. ``short``

是否可以被卖空。

资产模块
^^^^^^^^^^^^^^^^^^

.. autoclass:: AlgoTrading.api.XSHGStock
   :members:
   :undoc-members:

.. autoclass:: AlgoTrading.api.XSHEStock
   :members:
   :undoc-members:

.. autoclass:: AlgoTrading.api.IFFutures
   :members:
   :undoc-members:

.. autoclass:: AlgoTrading.api.ICFutures
   :members:
   :undoc-members:

.. autoclass:: AlgoTrading.api.IHFutures
   :members:
   :undoc-members:

.. autoclass:: AlgoTrading.api.EXIndex
   :members:
   :undoc-members:

