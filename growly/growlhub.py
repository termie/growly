import logging
import threading
import urllib2

from growly import protocol

class GrowlHubWatcher(threading.Thread):
  """Class to maintain an updated cache of known Growl servers"""
  def __init__(self, relay, url, password=None):
    self.timer = threading.Event()
    self.interval = 2.0 # no point in checking more often
    self.relay = relay
    self.url = url
    self.password = password
    super(GrowlHubWatcher, self).__init__()

  def shutdown(self):
    self.timer.set()

  def run(self):
    """Main loop"""
    while 1:
      if self.timer.isSet(): return
      try:
        rv = urllib2.urlopen(self.url)
        data = rv.read()
        if data:
          packet = protocol.GrowlPacket(data, self.password)
          self.relay.notify(packet)
      except urllib2.HTTPError, e:
        logging.exception('Errr %s', e)

      self.timer.wait(self.interval)
