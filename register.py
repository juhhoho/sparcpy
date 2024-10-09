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


    def __repr__(self):
        groups = {
            "<global>": [f"%g{i}" for i in range(8)],
            "<output>": [f"%o{i}" for i in range(8)],
            "<local>": [f"%l{i}" for i in range(8)],
            "<input>": [f"%i{i}" for i in range(8)],
            "<special>": ["%sp", "%fp"]
        }

        reg_list = []
        for group, regs in groups.items():
            reg_list.append(f"{group}: " + ", ".join([f"[{reg}]: {self.registers[reg]}" for reg in regs]))
        return "\n".join(reg_list)