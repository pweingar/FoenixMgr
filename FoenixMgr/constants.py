CMD_READ_MEM = 0x00
CMD_WRITE_MEM = 0x01
CMD_PROGRAM_FLASH = 0x10
CMD_ERASE_FLASH = 0x11
CMD_ERASE_SECTOR = 0x12
CMD_PROGRAM_SECTOR = 0x13
CMD_STOP_CPU = 0x20
CMD_START_CPU = 0x21
CMD_ENTER_DEBUG = 0x80
CMD_EXIT_DEBUG = 0x81
CMD_BOOT_RAM = 0x90
CMD_BOOT_FLASH = 0x91
CMD_REVISION = 0xFE

DELAY_ERASE_SECTOR = 1          # Number of seconds to wait after issueing an ERASE_SECTOR command
DELAY_PROGRAM_SECTOR = 2        # Number of seconds to wait after issueing an PROGRAM_SECTOR command

BOOT_SRC_RAM = 0x00             # For F256jr Rev A -- boot from RAM 
BOOT_SRC_FLASH = 0x01           # For F256jr Rev A -- boot from Flash 

REQUEST_SYNC_BYTE = 0x55
RESPONSE_SYNC_BYTE = 0xAA

PGX_CPU_65816 = 0x01
PGX_CPU_680X0 = 0x02
PGX_CPU_65C02 = 0x03

PGX_OFF_SIG_START = 0
PGX_OFF_SIG_END = 3
PGX_OFF_VERSION = 3
PGX_OFF_ADDR_START = 4
PGX_OFF_ADDR_END = 8
PGX_OFF_DATA = 8
