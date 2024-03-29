
"""Minimalist Rendezvous Client for Python"""
__version__ = "0.2"
__author__ = "Rui Carmo (http://the.taoofmac.com)"
__copyright__ = "(C) 2004 Rui Carmo. Code under BSD License."

import socket
import SocketServer
import string
import struct

_MDNS_ADDR = '224.0.0.251'
_MDNS_PORT = 5353

class _ReplyHandler(SocketServer.DatagramRequestHandler):
  def handle(self):
    ip = self.client_address[0]
    if ip not in self.server.replies:
      self.server.replies.append(ip)

class ZeroconfListener(SocketServer.UDPServer):
  allow_reuse_address = True
  replies = []

  def __init__(self, bind='localhost', handler=_ReplyHandler):
    SocketServer.UDPServer.__init__(self, (bind, _MDNS_PORT), handler)

  def query(self, proto):
    self.data = struct.pack("!HHHHHH", 0, 0, 1, 0, 0, 0)
    # pack query
    parts = proto.split('.')
    if parts[-1] == '':
      parts = parts[:-1]
    for part in parts:
      utf = part.encode('utf-8')
      l = len(utf)
      self.data += struct.pack("B", l)
      self.data += struct.pack('!' + str(l) + 's', utf)
    self.data += struct.pack("B", 0)
    # query for any PTR records
    self.data += struct.pack("!BBH", 0, 12, 1)
    try:
      self.socket.sendto(self.data, 0, (_MDNS_ADDR, _MDNS_PORT))
    except:
      pass
    tenths = 0
    while tenths < 20:
      self.handle_request()
      tenths = tenths + 1
    return self.replies

  def server_bind(self):
    self.group = ('', _MDNS_PORT)
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
      self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except:
      pass
    self.socket.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 255)
    self.socket.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)
    try:
      self.socket.bind(self.group)
    except:
      pass
    addr_host = (socket.inet_aton(socket.gethostbyname(socket.gethostname()))
                 + socket.inet_aton('0.0.0.0'))
    self.socket.setsockopt(socket.SOL_IP,
                           socket.IP_MULTICAST_IF,
                           addr_host)
    addr_mdns = socket.inet_aton(_MDNS_ADDR) + socket.inet_aton('0.0.0.0')
    self.socket.setsockopt(socket.SOL_IP,
                           socket.IP_ADD_MEMBERSHIP,
                           addr_mdns)
    self.socket.settimeout(0.1)

