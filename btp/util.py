import random
import string


def rand_client_oid():
    # return uuid.uuid4()
    r = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))
    r = '{}-{}'.format(r[:4], r[5:])
    assert len(r) == 32
    return r
