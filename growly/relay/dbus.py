
from growly import dbusclient
from growly.relay import base as relay

class DBusRelay(relay.Relay):
  def notify(self, packet):
    dbusclient.send(packet)
