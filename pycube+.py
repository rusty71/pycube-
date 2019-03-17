# -*- coding: utf-8 -*-
"""
http://4pda.ru/forum/lofiversion/index.php?t633481-360.html
192.72.1.1/cgi-bin/multi-sel1.cgi
192.72.1.1/cgi-bin/multi-sel2.cgi
192.72.1.1/cgi-bin/multi-sel3.cgi
192.72.1.1/cgi-bin/multi-sel4.cgi

Видео открывается VideoLAN'ом (Media -> Open Network Stream или Ctrl+N), можно наверное также граббить каким нить rtmpdump-ом, доступны следующие потоки

192.72.1.1/cgi-bin/liveMJPEG - 320x184 - без звука, картинка маленькая
192.72.1.1/cgi-bin/liveRTSP/v2 - 320x184 - то же самое
192.72.1.1/cgi-bin/liveRTSP/av1 - 320x184 - аналогично, но присутствует звуковой стрим 32000 Hz
192.72.1.1/cgi-bin/liveRTSP/v1 - 640x360 - без звука, но дико рвет картинку при перемещениях камеры, иногда камера наглухо виснет, приходится перевключать
192.72.1.1/cgi-bin/liveRTSP/av2 - 640x360 - то же, но со звуком 32000 Hz
"""
"""
http://www.cobra.com/support/software-updates/downloads/cdr875g-firmware-update
"""
"""
firmware hack
https://antonovich.me/2015/1/27/mivue-fw-restore/en/
https://dashcamtalk.com/forum/threads/mivue-firmware-modification.18768/
"""
from PyQt4 import QtCore, QtGui, uic
import sys
import cv2
import threading
import urllib
import NetworkManager
import dbus
import dbus.mainloop.glib
import requests
import urllib

HTTP_TIMEOUT = 5

form_class = uic.loadUiType("cube+.ui")[0] 

def pretty_session(ses):
    print('{}\n{}\n{}\n\n{}\n{}\n{}\n{}\n{}\n{}'.format(
        '-----------REQUEST-----------',
        ses.request.method + ' ' + ses.request.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in ses.request.headers.items()),
        ses.request.body,
        '-----------RESPONSE-----------',
        str(ses.status_code) + ' ' + ses.reason,
        '-----------CONTENT------------',
        ses.content,
        '-------------END--------------',
    ))

'''
712
Require authentication for the requested operation
'''
'''
709
General Error
'''
'''
722
Invalid state
'''
'''723
Low Battery
'''

#cubeSession maintains http session for the cube
class cubeSession():
    def __init__(self, timer):
        #cancel session
        try:
            requests.get("http://192.72.1.1/cgi-bin/User.cgi?logout", timeout=HTTP_TIMEOUT)
        except requests.exceptions.ConnectionError:
            print("Unable to connect to camera")
        self.s = requests.Session()
        #~ self.s.stream = False
        #~ self.s.headers.update({'Connection': 'close', 'Accept-Encoding': ''})
        #~ self.s.headers.pop('Accept')
        self.timer = timer
        self.timer.timeout.connect(self.keepalive)
        self.timer.start(5000)

    def close(self):
        self.timer.stop()
        self.s.close()

    def get(self, page, params):
        r = None
        try:
            r = self.s.get("http://192.72.1.1/cgi-bin/%s.cgi" % (page), params = params, timeout=HTTP_TIMEOUT)
            pretty_session(r)
            if r.content.startswith(b"712"):
                print("ERRORROROROROROROROORORERRORROROROROROROROORORERRORROROROROROROROORORERRORROROROROROROROOROR")
                #~ print("Trying to reset session")
                #~ rr = requests.get("http://192.72.1.1/cgi-bin/User.cgi?logout", timeout=HTTP_TIMEOUT)
                #~ pretty_session(rr)
                #~ self.login()
        except requests.exceptions.ConnectionError:
            print("Unable to connect to camera")
        return r


    def login(self):
        params = urllib.parse.urlencode({"action": "login", "user": "admin", "pass": "admin"})
        r = self.get("User", params)

    def keepalive(self):
        self.login()    #FIXME: loses connection whithout
        params = urllib.parse.urlencode({"action": "get", "property": "Camera.Menu.Alert"})
        r = self.get("Alert", params)
        #Camera.Menu.Alert=4    Charging
        #Camera.Menu.Alert=8    Recording
        #Camera.Menu.Alert=16   NO SD card


    def record(self):
        params = urllib.parse.urlencode({"action": "set", "property": "Video", "value": "record_start"})
        r = self.get("Config", params)

    def stop(self):
        params = urllib.parse.urlencode({"action": "set", "property": "Video", "value": "record_stop"})
        r = self.get("Config", params)
    
    def setResolution(self, res):
        params = urllib.parse.urlencode({"action": "set", "property": "Videores", "value": res})
        r = self.get("Config", params)

    def getLastThumb(self):
        params = urllib.parse.urlencode({"action": "get", "property": "Camera.Record.TheLastFileName"})
        r = self.get("Config", params)
        if r.status_code == 200:
            filename = r.content[r.content.find("Camera.Record.TheLastFileName=")+len("Camera.Record.TheLastFileName="):-1]
            r = self.s.get('http://192.72.1.1/thumb/DCIM/%s' % (filename))            
            qimg = QtGui.QImage()
            qimg.loadFromData(r.content)
            return(qimg)

    def getLastRec(self):
        params = urllib.parse.urlencode({"action": "get", "property": "Camera.Record.TheLastFileName"})
        r = self.get("Config", params)
        if r.status_code == 200:
            filename = r.content[r.content.find("Camera.Record.TheLastFileName=")+len("Camera.Record.TheLastFileName="):-1]
            return QtCore.QUrl("http://192.72.1.1/DCIM/%s" %(filename))

#http://192.72.1.1/cgi-bin/Config.cgi?action=set&property=Video&value=record_start
#http://192.72.1.1/cgi-bin/Config.cgi?action=set&property=Video&value=record_stop
#http://192.72.1.1/cgi-bin/Config.cgi?action=get&property=Camera.Record.TheLastFileName
#http://192.72.1.1/thumb/DCIM/100DSCIM/M0760079.mp4
#http://192.72.1.1/DCIM/100DSCIM/M1280131.MP4
#http://192.72.1.1/cgi-bin/Config.cgi?action=set&property=Videores&value=1080P30
#keepalive, every 15s)
#http://192.72.1.1/cgi-bin/Alert.cgi?action=get&property=Camera.Menu.Alert
#ffplay -rtsp_transport udp -i rtsp://192.72.1.1/liveRTSP/av2

class cubeCapture(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.rtsp = cv2.VideoCapture("rtsp://192.72.1.1/liveRTSP/av2")
        #~ self.rtsp = cv2.VideoCapture("rtsp://192.72.1.1/liveRTSP/v2")   #CHECK: low latency MJPEG
        self.running = True

    def stop(self):
        self.running = False
        
    def run(self):
        while self.running:
            self.rtsp.grab()
            retval, img = self.rtsp.retrieve(0)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, byteValue = img.shape
            qimg = QtGui.QImage(img.data, width, height, byteValue*width, QtGui.QImage.Format_RGB888)
            self.emit(QtCore.SIGNAL('img'), qimg)

class CubeWifi():
    import uuid
    
    SSID = "cube+me"
    cube_conn = {u'802-11-wireless': {
                          u'mode': u'infrastructure',
                          u'security': u'802-11-wireless-security',
                          u'ssid': u'cube+me'},
     u'802-11-wireless-security': {u'auth-alg': u'open',
                                   u'group': [],
                                   u'key-mgmt': u'wpa-psk',
                                   u'pairwise': [],
                                   u'proto': [],
                                   u'psk': u'1234567890'},
     u'connection': {u'id': u'cube+me',
                     u'type': u'802-11-wireless',
                     u'uuid': str(uuid.uuid4())},
     u'ipv4': {u'method': u'auto'},
     u'ipv6': {u'method': u'auto'}
    }

    def __init__(self, onconnect, ondisconnect):
        self.connected = False
        self.activated = False
        self._onConnect = onconnect
        self._onDisConnect = ondisconnect

        self.devices = []
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)   #CHECK:move mainloop to toplevel?
        NetworkManager.NetworkManager.OnStateChanged(self.statechange)  #network manager state changed
        #find all wifi devices
        self.connections = NetworkManager.Settings.ListConnections()
        for dev in NetworkManager.NetworkManager.GetDevices():
            if dev.DeviceType != NetworkManager.NM_DEVICE_TYPE_WIFI:
                continue
            self.devices.append(dev)
        #select wifi device
        if len(self.devices):
            self.device = self.devices[0]   #TODO:only use first device
        else:
            print("no wifi devices found")

        active_wifi = [x.Connection for x  in NetworkManager.NetworkManager.ActiveConnections if x.Connection.GetSettings()['802-11-wireless']]
        if len(active_wifi) > 0:
            self.restore = active_wifi[0] #TODO: one first used
        else:
            self.restore = None

        #if connection with SSID exists, use it
        self.cube_connection = [x for x in self.connections if x.GetSettings()['connection']['id']==CubeWifi.SSID]   #TODO: more than one?
        if not self.cube_connection:
            #use connection template
            self.cube_connection = NetworkManager.Settings.AddConnection(CubeWifi.cube_conn)
        else:
            self.cube_connection = self.cube_connection[0]  #TODO: multiple connections?

        #check if already active
        if(self.cube_connection in [x.Connection for x in NetworkManager.NetworkManager.ActiveConnections]):
            self.activated = True
            self.connected = [(x.State==NetworkManager.NM_ACTIVE_CONNECTION_STATE_ACTIVATED) for x in NetworkManager.NetworkManager.ActiveConnections if x.Connection == self.cube_connection][0]
            if(self.connected):
                if self._onConnect:
                    self._onConnect()

    #Network manager status changes
    def statechange(self, nm, interface, signal, state):
        #~ print("Networkmanager State changed to %s" % NetworkManager.const('STATE', state))
        self.activated = False
        try:
            conn = [x for x in NetworkManager.NetworkManager.ActiveConnections if x.Connection == self.cube_connection]
        except:
            conn = []
        if len(conn) > 0:
            conn = conn[0]
            self.activated = True
            if conn.State == NetworkManager.NM_ACTIVE_CONNECTION_STATE_ACTIVATED:
                if(not self.connected):
                    if self._onConnect:
                        self._onConnect()
                self.connected = True
            else:
                print("Cube *Not* connected")
                self.connected = False
        else:
            print("Cube not in active connections, disconnect")
            if self.connected:
                self.disconnect()
                self.connected = False
            self.activated = False
            
    def connect(self):
        NetworkManager.NetworkManager.ActivateConnection(self.cube_connection, self.device, "/")

    def disconnect(self):
        if self.restore:
            if self.restore != self.cube_connection:
                NetworkManager.NetworkManager.ActivateConnection(self.restore, self.device, "/")

    def close(self):
        pass

class CubeWindow(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.startButton.clicked.connect(self.start_clicked)
        self.wireframe.clicked.connect(self.wire_clicked)
        self.preview_button.clicked.connect(self.getUrl)
        self.resBox.connect(self.radioButton_720_120, QtCore.SIGNAL("toggled(bool)"),self.set_resolution)
        self.resBox.connect(self.radioButton_720_60,  QtCore.SIGNAL("toggled(bool)"),self.set_resolution)
        self.resBox.connect(self.radioButton_720_30,  QtCore.SIGNAL("toggled(bool)"),self.set_resolution)
        self.resBox.connect(self.radioButton_1080_30, QtCore.SIGNAL("toggled(bool)"),self.set_resolution)
        self.resBox.connect(self.radioButton_1080_60, QtCore.SIGNAL("toggled(bool)"),self.set_resolution)
        self.resBox.connect(self.radioButton_1440_30, QtCore.SIGNAL("toggled(bool)"),self.set_resolution)
        self.wifi = CubeWifi(self.on_connect, self.on_disconnect)
        self.connected = False
        self.recording = False
        self.resolution = "1080P30" #default
        self.connect(self, QtCore.SIGNAL("preview_img"), self.show_preview)

    #called if wifi connection with cube stopped 
    def on_disconnect(self):
        self.session.close()
        self.capture_thread.stop()  #CHECK: not needed
        self.capture_thread.terminate()
        self.capture_thread.wait()
        self.connected = False

        self.startButton.setEnabled(True)
        self.startButton.setText('Connect')

    #called if wifi connection with cube established 
    def on_connect(self):
        self.session = cubeSession(QtCore.QTimer(self))
        self.session.login()
        self.capture_thread = cubeCapture()
        self.connect(self.capture_thread, QtCore.SIGNAL("img"), self.update_frame)
        self.capture_thread.start()
        self.connected = True

        self.startButton.setEnabled(True)
        self.startButton.setText('Disconnect')


    def getUrl(self):
        url = self.session.getLastRec()
        #~ url = QtCore.QUrl('http://some.domain.com/path')
        if not QtGui.QDesktopServices.openUrl(url):
            QtGui.QMessageBox.warning(self, 'Open Url', 'Could not open url')  

    def set_resolution(self):
        for res in  self.resBox.children():
            if res.isChecked():
                if self.resolution != res.text():
                    self.resolution = res.text()
                    self.session.setResolution(self.resolution)

    def start_clicked(self):
        if self.connected:
            self.session.close()
            self.capture_thread.stop()  #CHECK: not needed
            self.wifi.disconnect()
            self.startButton.setEnabled(True)
            self.startButton.setText('Connect')
            self.connected = False
        else:
            print("Connecting pressed...")
            self.wifi.connect()
            self.startButton.setText('Connecting...')
            self.startButton.setEnabled(False)

    def wire_clicked(self):
        if self.recording:
            self.session.stop()
            self.recording = False
            preview = self.session.getLastThumb()
            self.show_preview(preview)
        else:
            self.session.record()
            self.recording = True

    def update_frame(self, frame):
        pixmap = QtGui.QPixmap.fromImage(frame);
        self.frame.resize(frame.width(), frame.height())
        self.frame.setPixmap(pixmap)

    def show_preview(self, preview):
        pixmap = QtGui.QPixmap.fromImage(preview);
        #~ self.frame.resize(frame.width(), frame.height())
        self.preview_button.setIcon(QtGui.QIcon(pixmap))

    def closeEvent(self, event):
        self.session.stop()
        self.wifi.disconnect()

app = QtGui.QApplication(sys.argv)
w = CubeWindow(None)
w.setWindowTitle('Palaroid Cube+ capture tool')
w.show()
app.exec_()
