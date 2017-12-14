import asyncio

from btp import Account, util


async def main():
    acc = Account('tyz@xtc.huobip')

    # 获取账号 info
    info, err = await acc.get_info()
    if err:
        print('Get info failed...', err)
    else:
        print(info)

    # 下单
    ref_key = util.rand_ref_key()  # ref_key 为预设下单 id，方便策略后期跟踪
    order, err = await acc.place_order(con='bch.btc:xtc.huobip', price=0.00001, bs='b', amount=10, ref_key=ref_key)
    if err:
        print('Place order failed...', err)
    else:
        print(order)

    await asyncio.sleep(3)

    # 获取当前开放的 order
    p_list, err = await acc.get_pending_list()
    if err:
        print('Get pending list failed...', err)
    else:
        print(p_list)

    # 撤单
    res, err = await acc.cancel_use_ref_key(ref_key=ref_key)
    if err:
        print('cancel order failed...', err)
    else:
        print(p_list)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
