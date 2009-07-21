import threading

from growly import zeroconf
from growly.relay import base as relay

class ZeroconfWatcher(threading.Thread):
  """Class to maintain an updated cache of known Growl servers"""
  def __init__(self):
    self.servers = []
    self.timer = threading.Event()
    self.interval = 120.0 # no point in checking more often

    threading.Thread.__init__(self)

  def shutdown(self):
    self.timer.set()

  def run(self):
    """Main loop"""
    p = zeroconf.ZeroconfServerListener()
    while 1:
      if self.timer.isSet(): return
      self.servers = p.query('_growl._tcp.local.')
      self.timer.wait(self.interval)

def ZeroconfRelay(relay.Relay):
  _base_servers = None

  def __init__(self, *args, **kw):
    self.watcher = ZeroconfWatcher()
    self.watcher.start()
    relay.Relay.__init__(self, *args, **kw)

  def _set_servers(self, value):
    self._base_servers = value

  def _get_servers(self):
    base_set = set(self._base_servers)
    base_set.add(self.watcher.servers)
    return base_set

  servers = property(_get_servers, _set_servers)

  def server_close(self):
    self.watcher.shutdown()
