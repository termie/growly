from growly import server
from growly import client

class RelayHandler(server.RequestHandler):
  discard_invalid = True

  def handle(self):
    packet = self.read_packet()
    if self.discard_invalid and not packet.valid:
      return
    self.server.notify(packet)


class Relay(server.Server):
  servers = None
  def __init__(self, servers=None, password=None, bind=None,
               handler=RelayHandler):
    if servers is None:
      servers = []
    self.servers = servers
    server.Server.__init__(self,
                           password=password,
                           bind=bind,
                           handler=handler)

  def notify(self, packet):
    sock = client.get_socket()
    for host in self.servers:
      client.send(host, packet, sock)
    sock.close()
