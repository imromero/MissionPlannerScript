from MissionPlannerIntegrator import MissionPlannerIntegrator
import logging
import sys
import time

# Set up the global logger for Mission Planner
logger = logging.getLogger("MissionPlanner")
logger.setLevel(logging.INFO)

# File handler: write logs to "mission_planner.log"
file_handler = logging.FileHandler("mission_planner.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Stream handler: output logs to the console (stdout)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)

logger.info("Logger configured: output to console and file 'mission_planner.log'.")


def Main():
    mp = MissionPlannerIntegrator()
    mp.Start()

if __name__ == "__main__":
    Main()