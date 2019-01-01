import re
from subprocess import Popen, PIPE


def get_MAC_address(IP):
    pid = Popen(["arp", "-n", IP], stdout=PIPE)
    s = pid.communicate()[0].decode()
    res = re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", s)
    if res is None:
        return None

    return res.groups()[0]
