# 名词解释

为了让之后文档的描述更加准确和清晰，对下列名词进行解释。具体数据结构请查看[数据结构](/instruction/data-structure)一节。

#### Zhubi

* 针对一条成交记录
* 逐笔(zhubi)成交记录，主要包含了该次交易的合约、成交时间、价格、成交量、方向（买或是卖）

#### Snapshot

* 针对1token的整个交易所
* 每隔一段时间（这个时间在0.5s到1s之间，是不确定的），1token会将整个market的状态保存为一个snapshot
* Snapshot中主要保存了当前各合约的**买卖档位**，以及从上一个snapshot到本次snapshot的**所有zhubi**


#### Tick

* 针对一个合约
* 每生成一个新的snapshot，1token将计算出一个新Tick
* 根据合约名聚合snapshot时刻的深度（asks,bids)
* 根据该合约最近时刻的zhubi得出最新成交价（last）
* 根据上一个snapshot到最新snapshot之间的所有zhubi统计出这段时间内的成交额（amount）以及成交量（volumn）