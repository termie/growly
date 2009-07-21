import threading

from growly import server
from growly import client
from growly import zeroconf

def RelayHandler(server.RequestHandler):
  discard_invalid = True

  def handle(self):
    packet = self.read_packet()
    if self.discard_invalid and not packet.valid:
      return

    sock = client.get_socket()
    for host in self.server.servers:
      client.send(host, packet, sock)
    sock.close()


def Relay(server.Server):
  servers = None
  def __init__(self, servers=None, password=None, bind=None,
               handler=RelayHandler):
    if servers is None:
      servers = []
    self.servers = servers
    super(Relay, self).__init__(password=password,
                                bind=bind,
                                handler=handler)


class ZeroconfWatcher(threading.Thread):
  """Class to maintain an updated cache of known Growl servers"""
  def __init__(self):
    self.servers = []
    self.timer = threading.Event()
    self.interval = 120.0 # no point in checking more often

    super(ZeroconfWatcher, self).__init__()

  def shutdown(self):
    self.timer.set()

  def getServers(self):
    return self.servers

  def run(self):
    """Main loop"""
    p = zeroconf.ZeroconfServerListener()
    while 1:
      if self.timer.isSet(): return
      self.servers = p.query('_growl._tcp.local.')
      self.timer.wait(self.interval)


def ZeroconfRelay(Relay):
  _base_servers = None

  def __init__(self, *args, **kw):
    self.watcher = ZeroconfWatcher()
    self.watcher.start()
    super(ZeroconfRelay, self).__init__(*args, **kw)

  def _set_servers(self, value):
    self._base_servers = value

  def _get_servers(self):
    base_set = set(self._base_servers)
    base_set.add(self.watcher.servers)
    return base_set

  servers = property(_get_servers, _set_servers)
