#!/usr/bin/env python3
"""
MAVLink Server Emulator using shared configuration (relative imports)
----------------------------------------------------------------------
This script is located in the "src/simulators" folder and uses relative imports
to load the configuration from the XML file located in the project root.
It creates a MAVLink connection and sends a heartbeat message every second.
"""

import time
import logging
import sys
import os
from pymavlink import mavutil

# Use relative import to load the configuration manager from the main package.
from ..ConfigLoader import ConfigLoader

class MavlinkServerEmulator:
    def __init__(self):
        # Compute the absolute path to the configuration file.
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config.xml"))
        logging.debug("Computed config path: %s", config_path)
        # Load the configuration using the shared configuration manager.
        self.config = ConfigLoader(config_path)
        
        # Retrieve the MAVLink connection string from the configuration.
        self.connection_string = self.config.mavlinkConnection_
        logging.debug("Using MAVLink connection string: %s", self.connection_string)
        
        # Create the MAVLink connection using the connection string.
        self.connection = mavutil.mavlink_connection(self.connection_string)
    
    def run(self):
        # Wait for a heartbeat from a client to ensure the connection is active.
        logging.debug("Waiting for client heartbeat...")
        self.connection.wait_heartbeat(timeout=30)
        logging.debug("Heartbeat received. Starting MAVLink server emulation.")
        
        while True:
            # Send a heartbeat message.
            self.connection.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_GCS,         # Emulate a Ground Control Station
                mavutil.mavlink.MAV_AUTOPILOT_INVALID,  # Indicate an invalid autopilot
                0, 0, 0
            )
            logging.debug("Heartbeat sent.")
            time.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s [%(levelname)s] %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")
    try:
        emulator = MavlinkServerEmulator()
        emulator.run()
    except KeyboardInterrupt:
        logging.debug("MAVLink Server Emulator terminated.")
        sys.exit(0)
