
# test class
from inspector import *

path= r"D:\project-internship\new2\StageMahdi\data\nvi\20230810\color.kinect"

inspector = Inspector(path=path, enable_report=True, json_fn = 'report')
res = inspector.run()

if res == True:
    print("WOW")
else:
    print("BAD")