from collections import defaultdict

try:
    import pyudev
except ImportError:
    pyudev = None


class UdevMonitor:
    def __init__(self, py3_wrapper):
        """
        """
        self.enabled = pyudev is not None
        self.py3_wrapper = py3_wrapper
        self.udev_consumers = defaultdict(list)
        self.udev_observer = None

    def _setup_pyudev_monitoring(self):
        """
        """
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        self.udev_observer = pyudev.MonitorObserver(monitor, self._udev_event)
        self.udev_observer.start()
        self.py3_wrapper.log('udev monitoring enabled')

    def _udev_event(self, action, device):
        """
        """
        self.refresh_subscribers(device.subsystem)

    def add_consumer(self, py3_module, subsystem):
        """
        """
        if self.enabled:
            # lazy load the udev monitor
            if self.udev_observer is None:
                self._setup_pyudev_monitoring()
            self.udev_consumers[subsystem].append(py3_module)
            self.py3_wrapper.log('module %s subscribed to udev events on %s' % (py3_module._module_full_name, subsystem))
            return True
        else:
            self.py3_wrapper.log('could not subscribe module %s to udev events on %s' % (py3_module._module_full_name, subsystem))
            return False

    def refresh_subscribers(self, subsystem):
        """
        """
        for py3_module in self.udev_consumers[subsystem]:
            self.py3_wrapper.log('%s udev event, refresh consumer %s' % (subsystem, py3_module._module_full_name))
            py3_module.update()
