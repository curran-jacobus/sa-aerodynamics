# TODO:
#   - add a units flag in the initialization. If user is using feet, automatically convert stuff from ft to m
#   - add feature to load in a QGC or txt file as a Python dictionary, to allow conversion between files and editing
#   - add feature to edit or remove items from a Mission object
#   - add all MAVlink mission commands from common.xml

import os
import json

class Mission:
    # list of all commands: https://mavlink.io/en/messages/common.html
    # description of QGC file format: https://docs.qgroundcontrol.com/master/en/qgc-dev-guide/file_formats/plan.html

    defaultLatitude = 37.422321 # N. middle of lake lag
    defaultLongitude = -122.176101 # W. middle of lake lag

    # default QGroundControl (QGC) mission plan file
    # home position is latitude, longitude, and altitude (m). Cruise speed (m/s)
    def __init__(self, homePosition=[37.422759609253525, -122.17393969854749, 47], cruiseSpeed=15, missionItems=[],
                 globalPlanAltitudeMode=1, defaultAltitude=49):
        self.defaultAltitude = defaultAltitude # meters. based on altitude mode. default is relative to takeoff location
        self.globalPlanAltitudeMode=globalPlanAltitudeMode
        self.mission = {
            "fileType": "Plan",
            "geoFence": {
                "circles": [
                ],
                "polygons": [
                ],
                "version": 2
            },
            "groundStation": "QGroundControl",
            "mission": {
                "cruiseSpeed": cruiseSpeed, # default speed (m/s) for a fixed wing
                "firmwareType": 12,
                "globalPlanAltitudeMode": globalPlanAltitudeMode,
                "hoverSpeed": 5, # for multirotor
                "items": missionItems,
                "plannedHomePosition": homePosition, # array of [latitude, longitude, altitude MSL]
                "vehicleType": 10, # according to docs, this value is "1" for fixed wing
                "version": 2
            },
            "rallyPoints": { # secondary home locations, if failure will go to nearest rally point
                "points": [
                ],
                "version": 2
            },
            "version": 1
        }

    # adds a dictionary item to the mission. Automatically adjusts the jump IDs sequentially
    def addItem(self, item):
        self.mission["mission"]["items"].append(item)
        self.updateJumpIDs()

    # QGC mission uses jump IDs to identify item positions, if it has to jump back to some
    # specific command in the case of a loop. When appending a new waypoint or other item
    # to this list, the jump IDs, which are assigned sequentially from the first item down,
    # do not automatically changed, so wrote this to change them.
    # TECHNICALLY don't really need it, since items already assigned sequentially, but good
    # practice? Could just have the next appended item assigned the length of "items"
    # NOTES: must have an item start with jump ID zero. Looks like QGC orders based on the order
    # in the list, rather than the number of the jump ID, need to test.
    def updateJumpIDs(self):
        # need to be careful, if there is a DO_JUMP action, also need to update that event to reflect
        # the correct item to jump to

        for i in range(0, len(self.mission["mission"]["items"])):
            self.mission["mission"]["items"][i]["doJumpId"] = i + 1 # start at 1 because 0th item is home location

    # exports the mission object to the specified file path. must specify file name, but should automatically
    # put in the QGC directory on a user's computer
    def exportqgc(self, filename, folderpath="/Users/ConnorHoffman/Documents/QGroundControl/Missions"):
        # filename also supports .mission, .txt (compatibility with Mission Planner), .waypoints
        self.updateJumpIDs()

        # no folder path or file name validation, should add try except in future or santize inputs
        with open(os.path.join(folderpath, filename), "w", encoding='utf-8') as file:
            # exports to valid JSON, since a Python dictionary and JSON are not identical
            json.dump(self.mission, file, ensure_ascii=False, indent=4)

    # exports the mission object to the specified file path with specified
    # this exports a universal file format, as specified by MAVlink, to many ground control systems
    # https://mavlink.io/en/file_formats/
    def export(self, filepath):
        # filename also supports .mission, .txt (compatibility with Mission Planner), .waypoints
        self.updateJumpIDs()

        # no folder path or file name validation, should add try except in future or santize inputs
        # SHOULD BE FILE TYPE .txt FOR MAXIMUM COMPATIBILITY
        with open(filepath, "w") as file:
            file.write("QGC WPL 110\n") # header

            # sets home waypoint, starts every mission
            # not sure on altitude, Mission Planner defaults to 0
            file.write("0\t1\t0\t16\t0\t0\t0\t0\t"+str(self.mission["mission"]["plannedHomePosition"][0])+"\t"+
                       str(self.mission["mission"]["plannedHomePosition"][1])+"\t0\t1\n")
            for item in self.mission["mission"]["items"]:
                file.write(str(item["doJumpId"]) + "\t") # index of item
                file.write("0" + "\t") # waypoint number. need to figure out what this does
                file.write(str(item["frame"]) + "\t") # MAV_FRAME. type of command/position method
                file.write(str(item["command"]) + "\t")
                for param in item["params"]:
                    if param == None:
                        file.write("NaN" + "\t") # writes NaN when a param is None type, not sure if necessary
                    else:
                        file.write(str(param) + "\t") # append all parameters
                file.write(str(int(item["autoContinue"]))) # converts to string
                file.write("\n") # next line. file needs to end with a new line or Mission Planner adds random item

    # returns string of mission. returns raw Python dictionary, or JSON formatted if True
    def plaintext(self,jsonFormat=False):
        if jsonFormat:
            return json.dumps(self.mission)
        return str(self.mission)

    # -----------------------------------------------------------------------------------------
    # events

    # adds waypoint to mission object. latitude, longitude, and altitude(m). Altitude is default unless specified
    # MAV_CMD_NAV_WAYPOINT (16)
    # default latitude and longitude are the middle of Lake Lag. Much easier to edit waypoint location on the map
    # in QGC than to manually enter the points
    def addWaypoint(self, latitude=defaultLatitude, longitude=defaultLongitude, altitude=-1):
        # if no altitude specified, go with default
        if altitude == -1:
            altitude = self.defaultAltitude

        item = {"AMSLAltAboveTerrain": None, # changed from JSON "null". Altitude shown to user
                "Altitude": altitude,
                "AltitudeMode": self.globalPlanAltitudeMode, # seems to stay fixed for all items
                "autoContinue": True, # changed from JSON "true"
                "command": 16, # MAV_CMD, indicates the intended MAVLink command
                "doJumpId": 0, # command identifier, for DO_JUMP and similar. Default to zero, updateJumpIDs will change
                "frame": 3, # MAV_FRAME, 2 = mission command, 3 = coordinate relative to home position
                "params": [
                    0,
                    0,
                    0,
                    None, # changed from JSON "null"
                    latitude,
                    longitude,
                    altitude
                ],
                "type": "SimpleItem" # ComplexItems are QGC specific, documentation in provided link
                }

        self.addItem(item)

    # performs loiter for a set number of turns
    # MAV_CMD_NAV_LOITER_TURNS (18)
    # same with defaults above, easiest to edit these parameters in QGC so defaults posted here
    def addLoiterTurns(self, latitude=defaultLatitude, longitude=defaultLongitude, numOfTurns=1,
                       radius=10, altitude=-1):
        # if no altitude specified, go with default
        if altitude == -1:
            altitude = self.defaultAltitude

        item = {"AMSLAltAboveTerrain": None,  # changed from "null". Altitude shown to user
                    "Altitude": altitude,
                    "AltitudeMode": self.globalPlanAltitudeMode,  # seems to stay fixed for all items
                    "autoContinue": True,  # changed from JSON "true"
                    "command": 18,  # MAV_CMD, indicates the intended MAVLink command
                    "doJumpId": 0,  # command identifier, for DO_JUMP and similar. Default to zero, updateJumpIDs will change
                    "frame": 3,  # MAV_FRAME, 2 = mission command, 3 = coordinate relative to home position
                    "params": [
                        numOfTurns,
                        0, # I don't know what this one is, Mission Planner sets it to 5, which is out of range
                        radius, # if positive, clockwise. negative, counter-clockwise
                        None,  # changed from JSON "null". thought-provoking parameter
                        latitude,
                        longitude,
                        altitude
                    ],
                    "type": "SimpleItem"  # complexItems are QGC specific, documentation in provided link
                    }

        self.addItem(item)

    # command to change the speed of the aircraft
    # MAV_CMD_DO_CHANGE_SPEED (178)
    # not really sure what difference between throttle and speed is, need to test
    # don't need an altitude param, but still takes one in? wonder if it will change something
    def addChangeSpeed(self, speed=-1, throttle=-1):
        altitude = self.defaultAltitude

        item = {"AMSLAltAboveTerrain": None,  # changed from "null". Altitude shown to user
                "Altitude": altitude,
                "AltitudeMode": self.globalPlanAltitudeMode,  # seems to stay the same for all items
                "autoContinue": True,  # changed from JSON "true"
                "command": 178,  # MAV_CMD, indicates the intended MAVLink command
                "doJumpId": 0, # command identifier, for DO_JUMP and similar. Default to zero, updateJumpIDs will change
                "frame": 2,  # MAV_FRAME, 2 = mission command, 3 = coordinate relative to home position
                "params": [
                    1, # SPEED_TYPE. indicates the way speed is measured. ground speed(1), should change to air(0)
                    speed,  # speed (m/s)
                    throttle,  # throttle (%)
                    0,
                    0,
                    0,
                    0
                ],
                "type": "SimpleItem"  # complexItems are QGC specific, documentation in provided link
                }

        self.addItem(item)