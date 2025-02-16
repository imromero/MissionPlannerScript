"""
Module: main.py
Description: Entry point for the Mission Planner application.
"""

from MissionPlanner import MissionPlanner

def Main():
    mp = MissionPlanner()
    mp.Start()

if __name__ == "__main__":
    Main()