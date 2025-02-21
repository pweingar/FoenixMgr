class MemoryBlock:
    """Represent a block of memory. Two MemoryBlocks that are contiguous can be collapsed into one."""
    
    def __init__(self, address, data):
        """Initialize the memory block"""
        self.set_address(address)
        self.set_data(data)

    def set_address(self, address):
        """Set the address of the memory block"""
        self._address = address

    def address(self):
        """Return the address of the memory block"""
        return self._address
    
    def set_data(self, data):
        """Set the data (and size) of the memory block"""
        self._data = data
        self._size = len(data)

    def data(self):
        """Return the data of the memory block"""
        return self._data
    
    def size(self):
        """Return the size of the data block"""
        return self._size
    
    def can_coalesce(self, block):
        """Return true if this block can coalesce with the given block"""
        if self.address() + self.size() == block.address():
            return True
        elif block.address() + block.size() == self.address():
            return True
        else:
            return False
        
    def coalesce(self, block):
        """Combine two memory blocks into one (they must be able to coalesce)"""
        if self.can_coalesce(block):
            if self.address() < block.address():
                new_data = self.data() + block.data()
                return MemoryBlock(self.address(), new_data)
            else:
                new_data = block.data() + self.data()
                return MemoryBlock(block.address(), new_data) 
        else:
            # These two blocks can't be combined!
            return 0

    def pad32(self):
        """Pad the memory block so that it starts and finishes on 32-bit aligned addresses"""

        # Check to see if the address starts on a 32-bit alignment
        addr_delta = self.address() % 4
        if addr_delta > 0:
            # If not, reduce the address to the next aligned address and pad the data
            self.set_address(self.address() - addr_delta)
            self.set_data((b"\0" * addr_delta) + self.data())

        # Check to see if the size ends the block on a 32-bit alignment
        size_delta = self.size() % 4
        if size_delta > 0:
            self.set_data(self.data() + (b"\0" * (4 - size_delta)))

    def output(self, chunk_size, handler):
        """Run the data in the memory block through the handler in chunks of the given size"""
        address = self.address()
        data = self.data()

        for i in range(0, self.size(), chunk_size):
            data_to_write = data[i:i+chunk_size]
            print("Address: 0x{0:08X}, Size: {1}".format(address + i, len(data_to_write)))
            handler(address + i, data_to_write)

class MemoryBlockList:
    def __init__(self):
        """Initialize the memory block list."""
        self._blocks = []

    def add(self, address, data):
        """Add a new block of data to the memory block list"""
        self._blocks.append(MemoryBlock(address, data))

    def blocks(self):
        """Return the list of all the memory blocks"""
        return self._blocks
    
    def pad32(self):
        """Align all memory blocks so they start and finish on 32-bit aligned addresses."""
        for block in self.blocks():
            block.pad32()

    def coalesce(self):
        """Combine all contiguous memory blocks."""

        # Make sure all the blocks are in order of address
        self._blocks.sort(key = lambda x : x.address())

        # Go block by block and coalesce them if possible
        new_blocks = []
        block = self._blocks.pop(0)
        while len(self._blocks) > 0:
            next_block = self._blocks.pop(0)
            if block.can_coalesce(next_block):
                block = block.coalesce(next_block)
            else:
                new_blocks.append(block)
                block = next_block

        # Make sure the last block is added back to the list
        new_blocks.append(block)

        # Reset the block list
        self._blocks = new_blocks

    def output(self, chunk_size, handler):
        """Send all data in the memory blocks to the handler"""

        for block in self.blocks():
            block.output(chunk_size, handler)
