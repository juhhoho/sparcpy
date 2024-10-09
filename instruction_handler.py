class InstructionHandler:
    def __init__(self, simulator):
        self.simulator = simulator

    def handle_instruction(self, instruction):
        command = instruction.split()[0]
        if command == "ld" or command == "st":
            self.handle_memory_access(instruction)
        else:
            handler = getattr(self, f"handle_{command}", None)
            if handler:
                handler(instruction)

    def handle_memory_access(self, instruction):
        operation, arg1, arg2 = instruction.split()
        if operation == "ld":
            print(f"[before register_state]\n{self.simulator.registers}\n")
            print(f"[before cache state]\n{self.simulator.cache}\n")
            print(f"[before memory_state]\n{self.simulator.memory}\n")
            address = self.parse_address(arg1)
            value = self.simulator.cache.access_cache(address)
            self.simulator.registers.set(arg2.strip(','), value)
            print(f"[after register_state]\n{self.simulator.registers}\n")
            print(f"[after cache state]\n{self.simulator.cache}\n")
            print(f"[after memory_state]\n{self.simulator.memory}\n")
        elif operation == "st":
            print(f"[before register_state]\n{self.simulator.registers}\n")
            print(f"[before cache state]\n{self.simulator.cache}\n")
            print(f"[before memory_state]\n{self.simulator.memory}\n")
            address = self.parse_address(arg2)
            value = self.simulator.registers.get(arg1.strip(','))
            self.simulator.cache.write_cache(address, value)
            print(f"[after register_state]\n{self.simulator.registers}\n")
            print(f"[after cache state]\n{self.simulator.cache}\n")
            print(f"[after memory_state]\n{self.simulator.memory}\n")

    def parse_address(self, mem_addr):
        base_reg, offset = mem_addr.strip('[],').split('+-')
        return self.simulator.registers.get(base_reg) - int(offset)

    def handle_mov(self, instruction):
        _, src, dest = instruction.split()
        src_value = int(src.strip(',')) if src.strip(',').isdigit() else self.simulator.registers.get(src.strip(','))
        self.simulator.registers.set(dest.strip(','), src_value)

    def handle_add(self, instruction):
        _, src1, src2, dest = instruction.split()
        self.simulator.registers.set(dest.strip(','), self.simulator.registers.get(src1.strip(',')) + self.simulator.registers.get(src2.strip(',')))

    def handle_save(self, instruction):
        _, src, offset, dest = instruction.split()
        self.save_register_state(int(offset.strip(',')))  # 여기서 save_register_state를 직접 호출

    def save_register_state(self, offset_value):
        sp_value = self.simulator.registers.get('%sp')
        new_sp = sp_value + offset_value
        if new_sp < 0:
            raise ValueError("스택 포인터가 음수입니다.")
        self.simulator.memory.write(new_sp, sp_value)  # 메모리에 스택 포인터 저장
        self.simulator.registers.set('%fp', sp_value)  # 프레임 포인터 업데이트
        self.simulator.registers.set('%sp', new_sp)  # 스택 포인터 업데이트

    def handle_ret(self, instruction):
        if self.simulator.call_stack:
            return_address = self.simulator.registers.get('%i7')
            self.simulator.program_counter = return_address
        else:
            print("No return address found, ready for ending program.")

    def handle_restore(self, instruction):
        if instruction != "restore":
            regs = [reg.strip(',') for reg in instruction.split()[1:]]
            self.simulator.registers.set(regs[2], self.simulator.registers.get(regs[0]) + self.simulator.registers.get(regs[1]))

        self.simulator.memory.write(self.simulator.registers.get('%sp'), 0)
        self.simulator.registers.set('%sp', self.simulator.registers.get('%fp'))

        if self.simulator.memory.read(self.simulator.registers.get('%fp')) == 0:
            self.simulator.registers.set('%fp', self.simulator.memory.size - 1)
        else:
            self.simulator.registers.set('%fp', self.simulator.memory.read(self.simulator.registers.get('%fp')))

    def handle_call(self, instruction):
        _, label_name = instruction.split()
        return_address = self.simulator.program_counter + 1
        self.simulator.call_stack.append(return_address)
        self.simulator.registers.set('%i7', return_address)

        if label_name in self.simulator.instructions:
            print(f"****************** label - <{label_name}> call******************")
            self.simulator.execute(label_name)
            self.simulator.program_counter = self.simulator.call_stack.pop() - 1
            print(f"******************label - <{label_name}> return******************")
        else:
            raise ValueError(f"함수 {label_name}을(를) 찾을 수 없습니다.")
