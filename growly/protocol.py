import md5
import struct

UDP_PORT=9887
PROTOCOL_VERSION=1
TYPE_REGISTRATION=0
TYPE_NOTIFICATION=1

class GrowlPacket(object):
  """Performs basic decoding of a Growl UDP Packet."""

  def __init__(self, data, password=None):
    """Initializes and validates the packet"""
    self.valid = False
    self.data = data
    self.digest = self.data[-16:]
    checksum = md5.new()
    checksum.update(self.data[:-16])
    if password:
      checksum.update(password)
    if self.digest == checksum.digest():
      self.valid = True

  def type(self):
    """Returns the packet type"""
    if self.data[1] == '\x01':
      return 'NOTIFY'
    else:
      return 'REGISTER'

  def info(self):
    """Returns a subset of packet information"""
    if self.type() == 'NOTIFY':
      nlen = struct.unpack("!H", str(self.data[4:6]))[0]
      tlen = struct.unpack("!H", str(self.data[6:8]))[0]
      dlen = struct.unpack("!H", str(self.data[8:10]))[0]
      alen = struct.unpack("!H", str(self.data[10:12]))[0]
      return struct.unpack("%ds%ds%ds%ds" % (nlen, tlen, dlen, alen),
                           self.data[12:len(self.data) - 16])
    else:
      length = struct.unpack("!H", str(self.data[2:4]))[0]
      return self.data[6:7 +length]


class GrowlNotificationPacket:
  """Builds a Growl Network Notification packet.
     Defaults to emulating the command-line growlnotify utility."""

  def __init__(self, application="growlnotify",
               notification="Command-Line Growl Notification", title="Title",
               description="Description", priority=0, sticky=False,
               password=None):
    self.application = application.encode("utf-8")
    self.notification = notification.encode("utf-8")
    self.title = title.encode("utf-8")
    self.description = description.encode("utf-8")
    flags = (priority & 0x07) * 2
    if priority < 0:
      flags |= 0x08
    if sticky:
      flags = flags | 0x0100
    self.data = struct.pack("!BBHHHHH",
                            PROTOCOL_VERSION,
                            TYPE_NOTIFICATION,
                            flags,
                            len(self.notification),
                            len(self.title),
                            len(self.description),
                            len(self.application))
    self.data += self.notification
    self.data += self.title
    self.data += self.description
    self.data += self.application
    self.checksum = md5.new()
    self.checksum.update(self.data)
    if password:
       self.checksum.update(password)
    self.data += self.checksum.digest()

  def payload(self):
    """Returns the packet payload."""
    return self.data


class GrowlRegistrationPacket:
  """Builds a Growl Network Registration packet.
     Defaults to emulating the command-line growlnotify utility."""

  def __init__(self, application="growlnotify", password=None):
    self.notifications = []
    self.defaults = [] # array of indexes into notifications
    self.application = application.encode("utf-8")
    self.password = password

  def addNotification(self, notification="Command-Line Growl Notification", enabled=True):
    """Adds a notification type and sets whether it is enabled on the GUI"""
    self.notifications.append(notification)
    if enabled:
      self.defaults.append(len(self.notifications) - 1)


  def payload(self):
    """Returns the packet payload."""
    self.data = struct.pack("!BBH",
                            PROTOCOL_VERSION,
                            TYPE_REGISTRATION,
                            len(self.application))
    self.data += struct.pack("BB",
                             len(self.notifications),
                             len(self.defaults))
    self.data += self.application
    for notification in self.notifications:
      encoded = notification.encode("utf-8")
      self.data += struct.pack("!H", len(encoded))
      self.data += encoded
    for default in self.defaults:
      self.data += struct.pack("B", default)
    self.checksum = md5.new()
    self.checksum.update(self.data)
    if self.password:
       self.checksum.update(self.password)
    self.data += self.checksum.digest()
    return self.data
