# pycube+

pycube is a python application for controlling the Polaroid Cube+ action camera.
The official Android app stopped working on my phone so I decided to try to reverse engineer the Cube+ protocol. The main inspiration was found on Reddit : https://www.reddit.com/r/PolaroidCube/comments/3vb0bn/streaming_video_from_cube_to_pc_easy/. I then started to tcpdump the traffic between my phone and the cube (see the pcap directory).
The resulting application is currently very barebones with lots of bugs  : https://vimeo.com/242809446 
For me this was an effort to learn about the NetworkManager, QT, OpenCV and to get my little actionCAM working again.

Requirements:
  *python-networkmanager  (for controlling your wifi)
  *python-opencv          (for view finder rtsp stream)
  *PyQT4
 
