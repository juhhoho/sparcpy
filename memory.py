class Memory:
    def __init__(self, size=256):
        self.memory = [0] * size
        self.size = size
    def read(self, address):
        if address < 0 or address >= len(self.memory):
            raise ValueError(f"Invalid memory address: {address}")
        return self.memory[address]

    def write(self, address, value):
        if address < 0 or address >= len(self.memory):
            raise ValueError(f"Invalid memory address: {address}")
        self.memory[address] = value

    def __repr__(self):
        # 메모리를 8개씩 끊어서 문자열로 변환
        return "\n".join(f"{int(i/8)}: " + str(self.memory[i:i + 8]) for i in range(0, len(self.memory), 8))
