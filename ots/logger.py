import sys
import logging

log = logging.getLogger('ots')


def set_log():
    import logging as syslog
    # syslog.basicConfig()
    ch = syslog.StreamHandler(sys.stdout)
    ch.setLevel(syslog.INFO)
    ch.setFormatter(
        syslog.Formatter('%(levelname)-.4s [%(asctime)s][qb][%(filename)s:%(lineno)s] %(message)s', '%H:%M:%S'))
    log.addHandler(ch)
    log.setLevel(syslog.INFO)

    def wrap(orig):
        def new_func(*args, **kwargs):
            # print('-------wrapper----------', args, kwargs)
            left = ' '.join(str(x) for x in args)
            right = ' '.join('{}={}'.format(k, v) for k, v in kwargs.items())
            new = ' '.join(filter(None, [left, right]))
            orig(new)

        return new_func

    log.info = wrap(log.info)
    log.warning = wrap(log.warning)
    log.exception = wrap(log.exception)


set_log()


def log_level(level):
    print('set log level to {}'.format(level))
    log.setLevel(level)
