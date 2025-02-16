"""
Module: UDPChannel.py
Description: Defines the UDPChannel class for abstracting UDP communications.
"""

import socket

class UDPChannel:
    """
    A simple wrapper around a UDP socket.
    
    Attributes:
        ip_ (str): Local IP.
        port_ (int): Port number.
        socket_ (socket.socket): The underlying UDP socket.
    """
    def __init__(self, ip, port, isReceiver=True):
        self.ip_ = ip
        self.port_ = port
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if isReceiver:
            self.socket_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_.bind((ip, port))
    
    def Send(self, data, targetIp, targetPort):
        """Sends data to the specified target."""
        self.socket_.sendto(data, (targetIp, targetPort))
    
    def Receive(self, bufsize=1024):
        """
        Receives data from the socket.
        
        Returns:
            tuple: (data, address)
        """
        return self.socket_.recvfrom(bufsize)