from memory import Memory
from register import Register
from cache import Cache
from instruction_handler import InstructionHandler  # 새로 추가된 부분

class SPARCSimulator:
    def __init__(self):
        self.memory = Memory()
        self.registers = Register(len(self.memory.memory))
        self.cache = Cache(self.memory)
        self.instructions = {}
        self.call_stack = []
        self.program_counter = 0
        self.instruction_handler = InstructionHandler(self)  # InstructionHandler 인스턴스 추가

        self.debug_info("#Start of Program ------------")
        print(f"[register init]:\n{self.registers}\n")
        print(f"[cache init]:\n{self.cache}\n")
        print(f"[memory init]:\n{self.memory}\n")

    def load_program_from_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                asm_code = f.readlines()

            current_label = None
            for line in asm_code:
                line = line.split('!')[0].strip()
                if not line:
                    continue
                if line.startswith('.'):
                    continue
                if ':' in line:
                    current_label = line.replace(':', '').strip()
                    self.instructions[current_label] = []
                elif current_label:
                    self.instructions[current_label].append(line)
        except FileNotFoundError:
            print(f"파일을 찾을 수 없습니다: {file_path}")
        except IOError:
            print(f"파일을 읽는 중 오류가 발생했습니다: {file_path}")

    def execute(self, label='main'):
        if label not in self.instructions:
            raise ValueError(f"라벨 '{label}'을(를) 찾을 수 없습니다.")

        self.program_counter = 0
        itr = 0
        instructions = self.instructions[label]

        while self.program_counter < len(instructions):

            if self.program_counter < itr and instructions[itr].startswith("restore"):
                self.instruction_handler.handle_restore(instructions[itr])
                self.program_counter -= 1
                self.debug_info()
                break

            instruction = instructions[self.program_counter]
            itr += 1

            print(f"현재 실행 중인 명령어: {label} - \"{instruction}\"")

            self.instruction_handler.handle_instruction(instruction)
            self.program_counter += 1

            self.debug_info()

        if label == 'main':
            self.debug_info("#End of program --------------")
            print(f"[register state]\n{self.registers}\n")
            print(f"[cache state]\n{self.cache}\n")
            print(f"[memory_state]\n{self.memory}\n")

    def debug_info(self, msg="#Info of Debug --------------"):
        print(msg)
        print(f"%sp: {self.registers.get('%sp')}")
        print(f"%fp: {self.registers.get('%fp')}")
        print(f"call_stack: {self.call_stack}")
        print(f"program_counter: {self.program_counter}")
        print("#-----------------------------")

    def parse_address(self, mem_addr):
        base_reg, offset = mem_addr.strip('[],').split('+-')
        return self.registers.get(base_reg) - int(offset)

    def save_register_state(self, offset_value):
        sp_value = self.registers.get('%sp')
        new_sp = sp_value + offset_value
        if new_sp < 0:
            raise ValueError("스택 포인터가 음수입니다.")
        self.memory.write(new_sp, self.registers.get('%sp'))
        self.registers.set('%fp', sp_value)
        self.registers.set('%sp', new_sp)


