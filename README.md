# skylink
UBC Unmanned Aircraft Systems Skylink Repository

#### Summary: 
Skylink acts as a relay between an RFD900 (Pixhawk) / SITL (Simulator) and a GCS program (QGroundcontrol / Missionplanner / Apm Planner).
It also intercepts mavlink (https://mavlink.io/en/guide/serialization.html) GPS packets and trees them to Smurfette and the Antenna Tracker software through a TCP connection.

#### Functional Requirements:
Have low latency relay between the Pixhawk/SITL and the GCS program (C++) mavlink library
Pixhawk hardware serial
SITL (http://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html) TCP serial
GCS TCP serial
Bidirectional
Send GPS packets to smurfette etc.
TCP serial
Pub / sub model (expose a port)
The format can be anything (JSON)
Latitude, Longitude, altitude (relative and absolute) (Consistent MSL / AGL), Heading (Compass direction (0 to 360)) , timestamp (epoch time, msg received)
If GPS hasn't been received in 0.5s, ask the pixhawk through the RFD (/tty/...) (GCS currently sends requests by MAVLink messages)
Basically, smurfette and antenna tracker should get their data without a GCS driving the messages.
Command-line arguments for port numbers
Automatically reconnect to any of the connects if they drop
Docker container
