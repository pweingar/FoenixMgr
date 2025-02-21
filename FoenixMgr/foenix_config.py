import configparser
import os
import sys

class FoenixConfig:
    """Configuration data for the FoenixMgr. Exposes the foenix.ini file."""

    def __init__(self):
        """Attempt to read and process the config file."""
        config = configparser.ConfigParser()
        config.read(['foenixmgr.ini', os.path.expandvars('$FOENIXMGR/foenixmgr.ini'), os.path.expanduser('~/foenixmgr.ini')])

        if not config.items("DEFAULT"):
            print("No proper foenixmgr.ini file found.")
            sys.exit(1)

        self._flash_size = int(config['DEFAULT'].get('flash_size', '524288'), 10)
        self._port = config['DEFAULT'].get('port', 'COM3')
        self._chunk_size = int(config['DEFAULT'].get('chunk_size', '4096'), 10)
        self._data_rate = int(config['DEFAULT'].get('data_rate', '6000000'), 10)
        self._label_file = config['DEFAULT'].get('labels', 'basic8')
        self._address = config['DEFAULT'].get('address', '380000')
        self._timeout = int(config['DEFAULT'].get('timeout', '60'), 10)
        self._cpu = config['DEFAULT'].get('cpu', '65c02')

    def set_target(self, machine_name):
        """Set the name of the target machine."""

        machine_name = machine_name.lower()

        self._flash_page_size = 0
        self._flash_sector_size = 0
        self._ram_size = 8

        if machine_name == "fnx1591":
            self._flash_page_size = 8
            self._ram_size = 8
            self._flash_sector_size = 32

        elif machine_name == "f256k" or machine_name == "f256jr":
            self._flash_page_size = 8
            self._ram_size = 8
            self._flash_sector_size = 8

    def flash_size(self):
        """Return the required size of the flash binary file in bytes."""
        return self._flash_size

    def chunk_size(self):
        """Return the size of the data packet that gets sent over the debug port."""
        return self._chunk_size

    def data_rate(self):
        """Return the data rate in bits per second that the serial port should use."""
        return self._data_rate

    def port(self):
        """Return the name of the port to use to connect to the debug port."""
        return self._port

    def label_file(self):
        """Return the name of the label file."""
        return self._label_file

    def address(self):
        """Return the address (in hex) to use in loading the flash file."""
        return self._address

    def timeout(self):
        """Return the timeout to allow for serial communications (in seconds)."""
        return self._timeout

    def cpu(self):
        """Return the CPU of the target machine."""
        return self._cpu
    
    def cpu_is_680X0(self):
        """Return true if the CPU is a Motorola 680X0"""
        if self.cpu() == "m68k" or self.cpu() == "68000" or self.cpu() == "68040" or self.cpu() == "68060":
            return True
        else:
            return False
        
    def cpu_is_m68k_32(self):
        """Return true if the CPU is a 32-bit Motorola 680X0"""
        if self.cpu() == "68040" or self.cpu() == "68060":
            return True
        else:
            return False

    def flash_page_size(self):
        """
        Return the size of the largest block of memory that can be copied to flash at one time (in KB).
        If zero, the machine does not support paged programming of the flash memory.
        """
        return self._flash_page_size

    def flash_sector_size(self):
        """
        Return the size of the flash sector (in KB).
        If zero, the machine does not support paged programming of the flash memory.
        """
        return self._flash_sector_size

    def ram_size(self):
        """
        Number of bytes in RAM that can be used to write to flash (in KB)
        """
        return self._ram_size