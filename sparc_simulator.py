from memory import Memory
from register import Register
from cache import Cache

class SPARCSimulator:
    def __init__(self):
        self.memory = Memory()
        self.registers = Register(len(self.memory.memory))  # 메모리 크기를 전달
        self.cache = Cache(self.memory)
        self.instructions = {}
        self.call_stack = []  # 호출 스택을 추가하여 PC 값을 관리
        self.program_counter = 0

    # .S 파일로부터 프로그램을 로드
    def load_program_from_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                asm_code = f.readlines()

            current_label = None
            for line in asm_code:
                line = line.split('!')[0].strip()  # 주석 제거
                if not line:  # 빈 줄 무시
                    continue
                if line.startswith('.'):  # 메타데이터 무시
                    continue
                if ':' in line:  # 라벨일 경우
                    current_label = line.replace(':', '').strip()
                    print(f"Label '{current_label}' found")  # 라벨 확인 로그 추가
                    self.instructions[current_label] = []
                elif current_label:  # 라벨 하위의 명령어일 경우
                    self.instructions[current_label].append(line)
            print()
        except FileNotFoundError:
            print(f"파일을 찾을 수 없습니다: {file_path}")
        except IOError:
            print(f"파일을 읽는 중 오류가 발생했습니다: {file_path}")

    # 프로그램을 실행
    def execute(self, label='main', debug=False):
        if label not in self.instructions:
            raise ValueError(f"라벨 '{label}'을(를) 찾을 수 없습니다.")

        self.program_counter = 0  # 해당 라벨에서 시작하는 프로그램 카운터
        itr = 0
        instructions = self.instructions[label]

        while self.program_counter < len(instructions):
            if self.program_counter < itr and instructions[itr].startswith("restore"):

                    self.handle_restore()
                    self.program_counter -= 1
                    print("#Debugging restore-----------")
                    print(f"%sp: {self.registers.get('%sp')}")
                    print(f"%fp: {self.registers.get('%fp')}")
                    print(f"call_stack: {self.call_stack}")
                    print(f"program_counter: {self.program_counter}")
                    print("#-----------------------------\n")
                    break

            instruction = instructions[self.program_counter]
            itr += 1

            self.handle_instruction(instruction)
            self.program_counter += 1

            if debug:
                print(f"현재 실행 중인 명령어: {label} - \"{instruction}\"")
            print("#Debugging -------------------")
            print(f"%sp: {self.registers.get('%sp')}")
            print(f"%fp: {self.registers.get('%fp')}")
            print(f"call_stack: {self.call_stack}")
            print(f"program_counter: {self.program_counter}")
            print("#-----------------------------\n")

    # 명령어 처리
    def handle_instruction(self, instruction):
        instruction = instruction.split("!")[0].strip()  # 주석 제거
        if instruction == "" or ":" in instruction:
            return  # 빈 라인 및 라벨 무시

        if instruction.startswith("ld"):
            _, mem_addr, reg = instruction.split()
            address = self.parse_address(mem_addr)
            value = self.cache.access(address)
            self.registers.set(reg.strip(','), value)
        elif instruction.startswith("st"):
            _, reg, mem_addr = instruction.split()
            address = self.parse_address(mem_addr)
            value = self.registers.get(reg.strip(','))
            self.memory.write(address, value)
        elif instruction.startswith("mov"):
            self.handle_mov(instruction)
        elif instruction.startswith("add"):
            self.handle_add(instruction)
        elif instruction.startswith("save"):
            self.handle_save(instruction)
        elif instruction.startswith("ret"):
            self.handle_ret()
        elif instruction.startswith("call"):
            self.handle_call(instruction)

    # mov 명령어 처리
    def handle_mov(self, instruction):
        _, src, dest = instruction.split()
        if src.strip(',').isdigit():
            src_value = int(src.strip(','))
        else:
            src_value = self.registers.get(src.strip(','))
        self.registers.set(dest.strip(','), src_value)

    # add 명령어 처리
    def handle_add(self, instruction):
        _, src1, src2, dest = instruction.split()
        val1 = self.registers.get(src1.strip(','))
        val2 = self.registers.get(src2.strip(','))
        self.registers.set(dest.strip(','), val1 + val2)

    # save 명령어 처리
    def handle_save(self, instruction):
        _, src, offset, dest = instruction.split()
        offset_value = int(offset.strip(','))
        sp_value = self.registers.get('%sp')
        new_sp = sp_value + offset_value

        if new_sp < 0:
            raise ValueError("스택 포인터가 음수입니다. 잘못된 스택 조정입니다.")

        # 현재 %fp 값을 새로운 스택 프레임에 저장
        self.memory.write(new_sp, self.registers.get('%fp'))  # 이전 %fp를 스택에 저장

        # 현재 %fp(sp_value) 값을 새로운 스택 프레임에 저장
        self.registers.set('%fp', sp_value)

        # 새로운 스택 포인터 설정
        self.registers.set('%sp', new_sp)


    # ret 명령어 처리
    def handle_ret(self):
        if not self.call_stack:
            print("No return address found, ending program.")
            return

        # 호출한 함수의 리턴 주소를 스택에서 꺼내기
        return_address = self.registers.get('%i7')

        # 리턴 주소로 프로그램 카운터 설정
        self.program_counter = return_address
        print(f"PC 복구: {self.program_counter}")

    # restore 명령어 처리
    def handle_restore(self):
        self.registers.set('%sp', self.registers.get('%fp'))
        self.registers.set('%fp', self.memory.read(self.registers.get('%fp')))

    # call 명령어 처리
    def handle_call(self, instruction):
        _, label_name = instruction.split()
        return_address = self.program_counter + 1  # 현재 PC 값을 저장
        self.call_stack.append(return_address)  # 호출 스택에 저장
        self.registers.set('%i7', return_address)  # %i7에 리턴 주소 저장
        if label_name in self.instructions:
            print(f"label - <{label_name}> call")
            self.program_counter = 0  # 새로운 함수 시작을 위해 프로그램 카운터를 0으로 초기화
            self.execute(label_name, True)  # 해당 라벨로 분기
            self.program_counter = self.call_stack[-1]
            self.call_stack.pop()
            self.program_counter -= 1
            print(f"label - <{label_name}> return")
        else:
            raise ValueError(f"함수 {label_name}을(를) 찾을 수 없습니다.")

    # 메모리 주소 해석
    def parse_address(self, mem_addr):
        mem_addr = mem_addr.strip('[],')
        base_reg, offset = mem_addr.split('+-')
        base_value = self.registers.get(base_reg)

        address = base_value - int(offset)  # 음수 오프셋 계산
        if address < 0:
            raise ValueError(f"Invalid memory address: {address}")

        return address


