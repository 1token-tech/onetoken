import asyncio
import os
import btp
import yaml
from btp import Account, util, log


def check_auth_file():
    path = os.path.expanduser('~/.qb/auth_config.yml')
    if not os.path.isfile(path):
        log.warn('auth config file is missing, attempt to create')
        username = input('Please enter your name: ')
        private_key_path = input('Please enter your private key path:')
        t_path = os.path.expanduser(private_key_path)
        while not os.path.isfile(t_path):
            log.warn('private key not existed...')
            private_key_path = input('Please enter your private key path:')
            t_path = os.path.expanduser(private_key_path)

        content = yaml.dump({'user': username, 'secret_path': private_key_path}, default_flow_style=False)
        with open(path, "w+") as f:
            f.write(content)
            f.close()


async def main():
    check_auth_file()

    acc = Account('leo@mock')

    # 获取账号 info
    info, err = await acc.get_info()
    if err:
        log.warning('Get info failed...', err)
    else:
        log.info(info)

    # 根据 pos symbol 获取账号 amount
    # 现货类似 btc, bch
    # 期货类似 btc.usd.q
    amount = acc.get_total_amount('btc')
    log.info(amount)

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
