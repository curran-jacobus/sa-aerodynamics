import mission

# example mission
testMission = mission.Mission()

# build waypoint that starts at 100% throttle, does two laps, decreased throttle by 5%, and repeats
for i in range(100,0,-5):
    testMission.addLoiterTurns(numOfTurns=2,radius=200)
    testMission.addChangeSpeed(throttle=i)

testMission.exportqgc("fixed_throttle_loiter_turns.plan")
testMission.export("~/Downloads/missiontxt.txt")
