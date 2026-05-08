# Learning **Kwargs
import subprocess
from sys import platform


# *args, takes the inputs as a tuple
# **kwargs takes the inputs as dictionary, keywords are given their value
'''def ping(**kwargs):
    """
    :param kwargs:
    -ip : the ip address
    -num : number of packets to send for ping, default set to 5
    -sn : ping sweep
    """

    for key, value in kwargs.items():
        print(key, value)

    if "-ip" in kwargs.keys():
        ip = kwargs["ip"]
    if "-num" in kwargs.keys():
        num_of_packets = kwargs["-p"]
    elif "-num" not in kwargs.keys():
        num_of_packets = 5

    # option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Build the command. ex: "ping -c 1 google.com"
    command = ['ping', param, str(num_of_packets), ip]

    return subprocess.call(command) == 0


# would this not be better to use *args
# a tuple of the commands used not a dictionary?
# this way -sn can be just -sn, ip='' can be its on value
# it would all be strings....
## ping(sn=True, ip="8.8.8.8")

'''


########################################################################################################################
# new attempt from learning from above

def ping(target="", *args):
    for value in args:
        print(value)
    command = ["ping", target]
    if "-sn" in args:
        print("-sn found in command")
        command += ["-sn"]
    print(command)


ping("google.com", "-sn")
