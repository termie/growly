
import socket

from growly import protocol

def get_socket():
  return socket.socket(socket.AF_INET, SOCK_DGRAM)


def send(host, packet, sock=None, close=False, port=protocol.UDP_PORT):
  if sock is None:
    sock = get_socket()
    close = True
  s.sendto(packet.data, (host, port))
  if close:
    s.close()

