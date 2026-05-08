# Connectivity checker

# Needs
# check website URL for successfully Pings
# check IPV4 for successfully Pings

# Wants
# Check IPV6 for successfully Pings
# Dictionary of success and non success via address as key

import platform, subprocess


def url_ping(url, num_of_packets):
    """ checker for connectivity to URL address
        returns True if host is up"""
    print("I will check ULR  for connectivity")

    # option for the number of packets as a function of

    # -n for windows pinging, -c for unix pinging
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Build the command. ex: "ping -c 1 google.com"
    command = ['ping', param, str(num_of_packets), url]

    # == 0 is to assume a successful connection is TRUE
    # == 1 is to assume an unsuccessful connection is TRUE
    # == 2 is to assume an ERROR/DNS errors is TRUE
    # subprocess is called so it executes the command and auto outputs to the console
    return subprocess.call(command) == 0


def ipv4_ping(ip, num_of_packets):
    """ checker for connectivity to IP address
        returns True if host is up"""
    print("I will check IP for connectivity")

    # option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Build the command. ex: "ping -c 1 google.com"
    command = ['ping', param, str(num_of_packets), ip]

    return subprocess.call(command) == 0


def dns_lookup(url):
    """ ns lookup for dns queries"""
    print("I will DNS query", url)

    #build command
    command = ['nslookup', url]

    return subprocess.call(command) == 0


#url_ping("google.com", 5)
#ipv4_ping("8.8.8.8", 5)
dns_lookup("google.com")
