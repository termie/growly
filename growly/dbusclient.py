import dbus

DEFAULT_ICON = '/usr/share/icons/gnome/scalable/categories/stock_internet.svg'

def get_service():
  bus = dbus.SessionBus()
  bus.get_object("org.freedesktop.DBus", "/org/freedesktop/DBus")
  notifyService = bus.get_object('org.freedesktop.Notifications',
                                 '/org/freedesktop/Notifications')
  return dbus.Interface(notifyService,
                        'org.freedesktop.Notifications')

def send(packet, service=None, icon=DEFAULT_ICON, expiration=-1):
  if packet.type() != 'NOTIFY':
    return
  if service is None:
    service = get_service()

  notification, title, description, app = packet.info()

  service.Notify(app, 0, icon, title, description, [], {}, expiration)
