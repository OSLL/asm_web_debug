import socket
import time

# Function parameters that are unlikely to be changed often
port_check_timeout = 1
port_probe_start = 1201
port_probe_max = 65535
port_probe_increment = 1

# Function that tries to open a port to check if it's available.
# Arguments:
#       ip [str] - IP address to connect to
#       port [str/int] - port to check
# Return value:
#       [bool] True if port is available, False otherwise.
def is_port_available(ip, port):
        try:
                sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sk.bind( (ip, port) )
                return True
        except (PermissionError, OSError):
                return False
        finally:
                sk.close()


# Functions that tries to find an open port in certain IP address.
# Arguments:
#       ip [str] - IP address to search through
# Return value:
#       [None] if maximum port number was exceeded and no open port was found
#       [int]  if an open port was found
def probe_for_port(ip):
        port = port_probe_start
        while (port <= port_probe_max) and (not is_port_available(ip, port)):
                port += port_probe_increment

        if port > port_probe_max:
                return None
        return port
