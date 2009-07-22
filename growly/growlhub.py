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

  def fetch_packets(self):
    rv = urllib2.urlopen(self.url)
    data = rv.read()
    if data:
      parts = data.split('\x00\x00\x00')
      return [protocol.GrowlPacket(part) for part in parts]
    return []

  def run(self):
    """Main loop"""
    while 1:
      if self.timer.isSet(): return
      try:
        packets = self.fetch_packets()
        for packet in packets:
          self.relay.notify(packet)
      except urllib2.HTTPError, e:
        logging.exception('Errr %s', e)

      self.timer.wait(self.interval)
