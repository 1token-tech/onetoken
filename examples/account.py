import asyncio

import btp
from btp import Account, util, log


async def main():
    acc = Account('tyz@xtc.huobip')

    # 获取账号 info
    info, err = await acc.get_info()
    if err:
        log.warning('Get info failed...', err)
    else:
        log.info(info)

    # 下单
    ref_key = util.rand_ref_key()  # ref_key 为预设下单 id，方便策略后期跟踪
    order, err = await acc.place_order(con='bch.btc:xtc.huobip', price=0.00001, bs='b', amount=10, ref_key=ref_key)
    if err:
        log.warning('Place order failed...', err)
    else:
        log.info(order)

    await asyncio.sleep(3)

    # 获取当前开放的 order
    p_list, err = await acc.get_pending_list()
    if err:
        log.warning('Get pending list failed...', err)
    else:
        log.info(p_list)

    # 撤单
    res, err = await acc.cancel_use_ref_key(ref_key=ref_key)
    if err:
        log.warning('cancel order failed...', err)
    else:
        log.info(p_list)

if __name__ == '__main__':
    import logging
    btp.log_level(logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())
