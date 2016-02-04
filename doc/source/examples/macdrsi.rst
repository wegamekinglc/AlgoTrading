.. _macd_rsi_doc:

MACD和RSI指标策略
------------------

让我们先看一下完整的代码和回测结果：

.. plot:: scripts/MACDRSI.py
   :include-source:

代码解析
^^^^^^^^^^^^^^^^^^

1. *指标*

这个策略使用了两个指标作为基本信号，在代码中为： ``MACDDIFF`` 以及 ``RSI``

   * ``MACDDIFF``

   以下的代码定义了 ``MACDDIFF`` 信号：

   .. code:: python

      MACDValue = MACD(fast, slow, 'close')
      AvgMACD = EMA(MACDLength, MACDValue)
      self.MACDDiff = MACDValue - AvgMACD

   本质上，这里的 ``MACDIFF`` 是基于收盘价的MACD当前值与MACD历史EMA均线的插值。

   * ``RSI``

   以下的代码定义了 ``RSI`` 信号：

   .. code:: python

      self.RSI = RSI(RSILength, 'close')

   这里 ``RSI`` 指标的时间长度为 ``RSILength``, 基于收盘价。

2. *开平仓条件*

   本策略在信号发出多头信号的时候，会调整仓位至多1手；而信号发出空头信号时，会调整仓位至空1手。

   * 开多仓条件

   .. code:: python

      if self.MACDDiff['000300.zicn'] > 2. \
                and self.RSI['000300.zicn'] > 51. \
                and self.secPos['000300.zicn'] != 1:
            self.order_to('000300.zicn', 1, 1)

   * 开空仓条件

   .. code:: python

      elif self.MACDDiff['000300.zicn'] < -2. \
                and self.RSI['000300.zicn'] < 49 \
                and self.secPos['000300.zicn'] != -1:



