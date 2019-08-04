from __future__ import print_function

import time

from pymavlink import mavutil
from argparse import ArgumentParser

parser = ArgumentParser(description=__doc__)
parser.add_argument("srcport", type=int)
parser.add_argument("dstport", type=int)

args = parser.parse_args()

msrc = mavutil.mavlink_connection('tcpin:localhost:{}'.format(args.srcport), planner_format=False,
                                  notimestamps=True,
                                  robust_parsing=True)

mdst = mavutil.mavlink_connection('tcp:localhost:{}'.format(args.dstport), planner_format=False,
                                  notimestamps=True,
                                  robust_parsing=True)


# simple basic byte pass through, no logging or viewing of packets, or analysis etc
# while True:
#  # L -> R
#    m = msrc.recv();
#    mdst.write(m);
#  # R -> L
#    m2 = mdst.recv();
#    msrc.write(m2);


# similar to the above, but with human-readable display of packets on stdout.
# in this use case we abuse the self.logfile_raw() function to allow
# us to use the recv_match function ( whch is then calling recv_msg ) , to still get the raw data stream
# which we pass off to the other mavlink connection without any interference.
# because internally it will call logfile_raw.write() for us.

# here we hook raw output of one to the raw input of the other, and vice versa:
msrc.logfile_raw = mdst
mdst.logfile_raw = msrc

while True:
  # L -> R
    l = msrc.recv_match();
    if l is not None:
        l_last_timestamp = 0
        if  l.get_type() != 'BAD_DATA':
            l_timestamp = getattr(l, '_timestamp', None)
            if not l_timestamp:
                l_timestamp = l_last_timestamp
            l_last_timestamp = l_timestamp

        print("--> %s.%02u: %s\n" % (
            time.strftime("%Y-%m-%d %H:%M:%S",
            time.localtime(l._timestamp)),
            int(l._timestamp*100.0)%100, l))

  # R -> L
    r = mdst.recv_match();
    if r is not None:
        r_last_timestamp = 0
        if r.get_type() != 'BAD_DATA':
            r_timestamp = getattr(r, '_timestamp', None)
            if not r_timestamp:
                r_timestamp = r_last_timestamp
            r_last_timestamp = r_timestamp

        if 'GLOBAL_POSITION' in r.get_type():
            print("<-- %s.%02u: %s\n" % (
                time.strftime("%Y-%m-%d %H:%M:%S",
                time.localtime(r._timestamp)),
                int(r._timestamp*100.0)%100, r))

