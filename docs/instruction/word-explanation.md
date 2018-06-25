# 名词解释

#### Zhubi

逐笔(zhubi)成交记录，主要包含了该次交易的合约、成交时间、价格、成交量、方向（买或是卖）。

#### Snapshot

每隔一段时间（这个时间在0.5s到1s之间，是不确定的），1token会将整个market的状态保存为一个快照（snapshot）。

Snapshot中主要保存了当前各合约的买卖档位，以及从上一个snapshot到本次snapshot的所有zhubi。


#### Tick

每生成一个新的snapshot，