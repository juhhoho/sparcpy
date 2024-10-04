class Memory:
    def __init__(self, size=256):
        self.memory = [0] * size

    def read(self, address):
        if address < 0 or address >= len(self.memory):
            raise ValueError(f"Invalid memory address: {address}")
        return self.memory[address]

    def write(self, address, value):
        if address < 0 or address >= len(self.memory):
            raise ValueError(f"Invalid memory address: {address}")
        self.memory[address] = value

    def __repr__(self):
        return str(self.memory)  # 배열 형태로 메모리 출력
