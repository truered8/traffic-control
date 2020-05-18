# traffic-control
A traffic control system in Python using PyGame and OpenCV.

# Setup
First, ensure that you have git, Python, and pip installed.
Then, install the dependencies:
```
pip install -r requirements.txt
```

# Usage
```
# allows user to select lanes
python lane_select.py -p {path to image of intersection} -s {path to save new image}

# runs vehicle detection example from https://github.com/andrewssobral/vehicle_detection_haarcascades
python vehicle_detection.py

# runs main simulation
python simtest.py
```
