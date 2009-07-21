#!/usr/bin/env python

"""Growl 0.6 DBUS Bridge"""
__version__ = "0.1"
__author__ = "Rui Carmo (http://the.taoofmac.com)"
__copyright__ = "(C) 2006 Rui Carmo. Code under BSD License."

import sys, os
import dbus
import dbus.glib
import gobject
from regrowl import GrowlPacket
from netgrowl import *
from SocketServer import *


class GrowlListener(UDPServer):
  """Growl Notification Listener"""
  allow_reuse_address = True

  def __init__(self, inpassword = None, outpassword = None):
    """Initializes the relay and launches the resolver thread"""
    self.inpassword = inpassword
    self.outpassword = outpassword
    bus = dbus.SessionBus()
    bus.get_object("org.freedesktop.DBus","/org/freedesktop/DBus")
    notifyService = bus.get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications')
    self.interface = dbus.Interface(notifyService, 'org.freedesktop.Notifications')
    UDPServer.__init__(self,('localhost', GROWL_UDP_PORT), _RequestHandler)
  # end def

  def server_close(self):
    self.resolver.shutdown()
  # end def
# end class


class _RequestHandler(DatagramRequestHandler):
  """Processes and each incoming notification packet"""

  def handle(self):
    """Handles each request"""
    p = GrowlPacket(self.rfile.read(), self.server.inpassword,self.server.outpassword)
    if p.type() == 'NOTIFY':
      notification,title,description,app = p.info()
      self.server.interface.Notify(app,0,'/usr/share/icons/gnome/scalable/categories/stock_internet.svg',title,notification,[],{},-1)

if __name__ == "__main__":
  r = GrowlListener('password','password')
  try:
    r.serve_forever()
  except KeyboardInterrupt:
    r.server_close()
