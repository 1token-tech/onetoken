"""
Usage:
    quote.py [options]

Options:
    --print-only-delay     Print only delay tick
    --test  test cases
"""
import time

import arrow
import logging
import onetoken_sync as ot
from onetoken_sync import Tick


class Config:
    print_only_delay = False
    test = False


def on_update_1(tk: Tick):
    delay = (arrow.now() - tk.time).total_seconds()
    if delay > 10:
        logging.warning('tick delay comes')
        print(arrow.now(), 'tick come 1', delay, tk)
    if not Config.print_only_delay:
        print(arrow.now(), 'tick come 1', delay, tk)


def on_update_2(tk: Tick):
    delay = (arrow.now() - tk.time).total_seconds()
    if delay > 10:
        logging.warning('tick delay comes')
        print(arrow.now(), 'tick come 2', delay, tk)
    if not Config.print_only_delay:
        print(arrow.now(), 'tick come 2', delay, tk)


def subscribe_from_ws():
    tick_v3 = ot.quote.get_v3_client()
    tick_v3.run()
    sub_list = ['okex/ltc.btc', 'okex/bch.btc']
    for contract in sub_list:
        tick_v3.subscribe_tick_v3(contract, on_update_1)

    contract = 'okex/btc.usdt'
    tick_v3.subscribe_tick_v3(contract, on_update_2)

    contract = 'binance/eth.btc'
    tick_v3.subscribe_tick_v3(contract, on_update_2)
    time.sleep(20)
    logging.warning('i am going to test reconnect')
    time.sleep(1)
    tick_v3.ws.close()
    time.sleep(20)
    tick_v3.close()


def get_last():
    contract = 'binance/btc.usdt'

    while True:
        tk, err = ot.quote.get_last_tick(contract)
        if err:
            logging.warning(err)
            continue
        delay = (arrow.now() - tk.time).total_seconds()
        if delay > 10:
            logging.warning('tick delay on get last')
        if not Config.print_only_delay:
            print(arrow.now(), 'tick get by last', delay, tk, err)


def main():
    # if you are in China Mianland, you can uncomment the following line to use another host
    # ot.Config.change_host()
    cons, err = ot.quote.get_contracts('binance')
    print(cons, err)
    con, err = ot.quote.get_contract('binance/btc.usdt')
    print(con, err)

    subscribe_from_ws()
    get_last()


if __name__ == '__main__':
    try:
        from docopt import docopt as docoptinit
    except ImportError:
        print('docopt not installed, run the following command first:')
        print('pip install docopt')
        import sys

        sys.exit(1)

    docopt = docoptinit(__doc__)
    Config.print_only_delay = docopt['--print-only-delay']
    Config.test = docopt['--test']
    print('ots folder', ot)
    print('ots version', ot.__version__)
    ot.log_level(logging.INFO)
    main()
