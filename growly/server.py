import logging
import SocketServer

from growly import protocol

class RequestHandler(SocketServer.DatagramRequestHandler):
  def read_packet(self):
    return protocol.GrowlPacket(self.rfile.read(), self.server.password)

  def handle(self):
    packet = self.read_packet()
    logging.info('received %s', packet)

class Server(SocketServer.UDPServer):
  allow_reuse_address = True

  def __init__(self, password=None, bind=None, handler=RequestHandler):
    self.password = password
    if bind is None:
      bind = ''

    # depending on your architecture and number of network interfaces,
    # you might have to change the '' below.
    SocketServer.UDPServer.__init__(self, (bind, protocol.UDP_PORT), handler)
