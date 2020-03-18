from __future__ import print_function

"""
Skylink is a relay between an RFD900(Pixhawk)/SITL(Simulator) and a GCS
(Ground control software) program (QGroundControl/Missionplanner).
It intercepts mavlink GPS packets and trees them between
Smurfette and the Antenna Tracker Software through a TCP connection.

e.g. the script can be run as 'python repeater.py [dstport] [srcport]'

"""

import time
import socket
import json
from pymavlink import mavutil
from argparse import ArgumentParser

#######################################################################
#                               HELPERS                               #
#######################################################################


def create_global_pos_dict(r):
    """
    Creates the dictionary to send with the required
    format to send to the desintation port

    :param r:
    :type r:
    :returns: global position dictionary with required field
    :rtype: dict

    """
    # create and send dict from global position
    send_dict = {'latitude': getattr(r, 'lat', None),
                 'longitude': getattr(r, 'lon', None),
                 'altitude_agl_meters': getattr(r, 'alt', None),
                 'altitude_msl_meters': getattr(r, 'relative_alt', None),
                 'heading_degrees': getattr(r, 'hdg', None),
                 'vel_x': getattr(r, 'vx', None),
                 'vel_y': getattr(r, 'vy', None),
                 'vel_z': getattr(r, 'vz', None),
                 'timestamp_telem': getattr(r, 'time_boot_ms', None),
                 'timestamp_msg': time.time()}
    return send_dict


#######################################################################
#                                MAIN                                 #
#######################################################################

if __name__ == "__main__":

    # arg parse setup and parsing
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("srcport", type=int)
    parser.add_argument("dstport", type=int)

    args = parser.parse_args()

    msrc = mavutil.mavlink_connection('tcpin:localhost:{}'
                                      .format(args.srcport),
                                      planner_format=False,
                                      notimestamps=True,
                                      robust_parsing=True)

    mdst = mavutil.mavlink_connection('tcp:localhost:{}'
                                      .format(args.dstport),
                                      planner_format=False,
                                      notimestamps=True,
                                      robust_parsing=True)

    # set up the server socket
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind(('', 4803))
    serv.listen(5)

    # Human-readable display of packets on stdout. In this use case we
    # abuse the self.logfile_raw() function to allow us to use the recv_match
    # function (whch is then calling recv_msg), to still get the raw data
    # stream which we pass off to the other mavlink connection without
    # any interference, because internally it will call logfile_raw.write()
    # for us

    # hook raw output of one to the raw input of the other, and vice versa:
    msrc.logfile_raw = mdst
    mdst.logfile_raw = msrc

    conn, addr = serv.accept()
    while True:
        # accept new connections
        # pixhawk/SITL -> R
        pixhawk_msg = msrc.recv_match()
        if pixhawk_msg is not None:
            pixhawk_last_timestamp = 0
            if pixhawk_msg.get_type() != 'BAD_DATA':
                pixhawk_timestamp = getattr(pixhawk_msg, '_timestamp', None)
                if not pixhawk_timestamp:
                    pixhawk_timestamp = pixhawk_last_timestamp
                pixhawk_last_timestamp = pixhawk_timestamp

            # # this prints data received from Pixhawk/SITL
            print("--> %s.%02u: %s\n" % (
                time.strftime("%Y-%m-%d %H:%M:%S",
                time.localtime(pixhawk_msg._timestamp)),
                int(pixhawk_msg._timestamp*100.0)%100, pixhawk_msg))

        # GCS  -> pixhawk/SITL and GCS -> server port
        gcs_msg = mdst.recv_match()
        if gcs_msg is not None:
            gcs_msg_last_timestamp = 0
            if gcs_msg.get_type() != 'BAD_DATA':
                gcs_msg_timestamp = getattr(gcs_msg, '_timestamp', None)
                if not gcs_msg_timestamp:
                    gcs_msg_timestamp = gcs_msg_last_timestamp
                gcs_msg_last_timestamp = gcs_msg_timestamp

            # this sends the position data on the server port
            if 'GLOBAL_POSITION' in gcs_msg.get_type():
                global_pos_dict = create_global_pos_dict(gcs_msg)
                print(global_pos_dict)
                conn.send(json.dumps(global_pos_dict))

            # this sends position data to the GCS
            if 'GLOBAL_POSITION' in gcs_msg.get_type():
                print("<-- %s.%02u: %s\n" % (
                    time.strftime("%Y-%m-%d %H:%M:%S",
                    time.localtime(gcs_msg._timestamp)),
                    int(gcs_msg._timestamp*100.0) % 100, gcs_msg))
                print(type(gcs_msg))

