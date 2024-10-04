class Register:
    def __init__(self, memory_size):
        self.registers = {f"%g{i}": 0 for i in range(8)}  # %g0 - %g7
        self.registers.update({f"%o{i}": 0 for i in range(8)})  # %o0 - %o7
        self.registers.update({f"%l{i}": 0 for i in range(8)})  # %l0 - %l7
        self.registers.update({f"%i{i}": 0 for i in range(8)})  # %i0 - %i7
        self.registers.update({'%sp': 0, '%fp': 0})  # 스택 포인터, 프레임 포인터

        # 스택 포인터와 프레임 포인터 초기화
        self.set('%sp', memory_size - 1)  # 스택을 메모리 끝에서 시작
        self.set('%fp', self.get('%sp'))  # 프레임 포인터를 스택 포인터와 일치시킴

    def get(self, reg):
        if reg not in self.registers:
            raise ValueError(f"Invalid register: {reg}")
        return self.registers[reg]

    def set(self, reg, value):
        if reg not in self.registers:
            raise ValueError(f"Invalid register: {reg}")
        self.registers[reg] = value

    # 레지스터와 값 포함 리스트
    def list_registers(self):
        reg_list = []
        for reg, value in self.registers.items():
            reg_list.append(f"{reg}: {value}")
        return reg_list
