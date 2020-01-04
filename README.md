## skylink
UBC Unmanned Aircraft Systems Skylink Repository 

#### Summary: 
- Skylink acts as a relay between an RFD900 (Pixhawk) / SITL (Dronekit Simulator) and a GCS program (QGroundcontrol / Missionplanner / Apm Planner).
- It also intercepts mavlink (https://mavlink.io/en/guide/serialization.html) GPS packets and trees them to Smurfette and the Antenna Tracker software through a TCP connection. (See confluence page for more details)

#### How To Use:
1. Run the SITL docker which acts as the Pixhawk would `docker run --rm -p 5760-5760:5760-5760 --env NUMCOPTERS=1 --env NUMROVERS=0 radarku/sitl-swarm` to display the SITL simulator which simulates the pixhawk on port `5760`
2. Run the skylink main python file as `python repeater.py [dstport] [srcport]` with `dstport = 5761` and `srcport = 5760` so `python repeater.py 5761 5760` to run Skylink listenting to the SITL pixhawk simulator docker ran in step 1 and then setup a server on port `5761` for the GCS mavlink connection. Additionally there is temporarily hardcoded port (soon to be another argument) to send the global position data over on a port to Smurfette and Antenna Tracker
3. Run `python client.py` to simulate a listener such as smurfette or antenna tracker which are clients for this data
4. Run QGroundControl Software and connect to 127.0.0.1:5761 and run the drone and you should see data on the client.py and repeater.py

#### Functional Requirements:
- Have low latency relay between the Pixhawk/SITL and the GCS program (C++) mavlink library
- Pixhawk hardware serial
- SITL (http://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html) TCP serial
- GCS TCP serial
- Bidirectional
-Send GPS packets to smurfette etc.
- TCP serial
- Pub / sub model (expose a port)
-The format can be anything (JSON)
- Latitude, Longitude, altitude (relative and absolute) (Consistent MSL / AGL), Heading (Compass direction (0 to 360)) , timestamp (epoch time, msg received)
- If GPS hasn't been received in 0.5s, ask the pixhawk through the RFD (/tty/...) (GCS currently sends requests by MAVLink messages)
- Basically, smurfette and antenna tracker should get their data without a GCS driving the messages.
- Command-line arguments for port numbers
- Automatically reconnect to any of the connects if they drop
- Runs as a docker container

#### To run SITL simlator:
Run `docker run --rm -p 5760-5760:5760-5760 --env NUMCOPTERS=1 --env NUMROVERS=0 radarku/sitl-swarm`
