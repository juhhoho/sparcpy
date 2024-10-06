from memory import Memory
from register import Register
from cache import Cache

class SPARCSimulator:
    def __init__(self):
        self.memory = Memory()
        self.registers = Register(len(self.memory.memory))  # 메모리 크기를 전달
        self.cache = Cache(self.memory, 16)
        self.instructions = {}
        self.call_stack = []  # 호출 스택을 추가하여 PC 값을 관리
        self.program_counter = 0

        self.debug_info("#Start of Program ------------")
        print(f"[memory init]:\n{self.memory}\n")
        print(f"[cache init]:\n{self.cache}\n")
        print(f"[register init]:\n{self.registers}\n")

    # .S 파일로부터 프로그램을 로드f
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
    def execute(self, label='main'):
        if label not in self.instructions:
            raise ValueError(f"라벨 '{label}'을(를) 찾을 수 없습니다.")

        self.program_counter = 0  # 해당 라벨에서 시작하는 프로그램 카운터
        itr = 0
        instructions = self.instructions[label]

        while self.program_counter < len(instructions):

            if self.program_counter < itr and instructions[itr].startswith("restore"):
                print(f"현재 실행 중인 명령어: {label} - \"{instructions[itr]}\"")
                self.handle_restore(instructions[itr])
                self.program_counter -= 1
                self.debug_info()
                break

            instruction = instructions[self.program_counter]
            itr += 1

            print(f"현재 실행 중인 명령어: {label} - \"{instruction}\"")

            self.handle_instruction(instruction)
            self.program_counter += 1

            self.debug_info()
            print(self.registers.registers, "\n")

        # 프로그램 종료
        if label == 'main':
            self.debug_info("#End of program --------------")
            print(f"[cache state]{self.cache}\n")
            print(f"[memory_state]\n{self.memory}\n")
            print(f"[register state]\n{self.registers}\n")

    # 디버깅 정보 출력
    def debug_info(self, msg = "#Info of Debug --------------"):
        print(msg)
        print(f"%sp: {self.registers.get('%sp')}")
        print(f"%fp: {self.registers.get('%fp')}")
        print(f"call_stack: {self.call_stack}")
        print(f"program_counter: {self.program_counter}")
        print("#-----------------------------")

    # 명령어 처리
    def handle_instruction(self, instruction):
        instruction = instruction.split("!")[0].strip()  # 주석 제거
        if instruction == "" or ":" in instruction:
            return  # 빈 라인 및 라벨 무시

        command = instruction.split()[0]
        if command == "ld" or command == "st":
            self.handle_memory_access(instruction)
        else:
            handler = getattr(self, f"handle_{command}", None)
            if handler:
                handler(instruction)

    # 메모리 접근 처리 (ld, st)
    def handle_memory_access(self, instruction):
        operation, arg1, arg2 = instruction.split()
        if operation == "ld":
            address = self.parse_address(arg1)
            print(f"[before cache state]\n{self.cache}\n")
            print(f"[before memory_state]\n{self.memory}\n")
            value = self.cache.access(address)
            self.registers.set(arg2.strip(','), value)
            print(f"[after cache state]\n{self.cache}\n")
            print(f"[after memory_state]\n{self.memory}\n")
        elif operation == "st":
            address = self.parse_address(arg2)
            print(f"[before cache state]\n{self.cache}\n")
            print(f"[before memory_state]\n{self.memory}\n")
            value = self.registers.get(arg1.strip(','))
            # 캐시를 먼저 접근하여 캐시가 있으면 갱신하고, 없으면 메모리로 쓰기 전에 캐시에 로드 후 갱신
            self.cache.write(address, value)
            print(f"[after cache state]\n{self.cache}\n")
            print(f"[after memory_state]\n{self.memory}\n")

    # mov 명령어 처리
    def handle_mov(self, instruction):
        _, src, dest = instruction.split()
        src_value = int(src.strip(',')) if src.strip(',').isdigit() else self.registers.get(src.strip(','))
        self.registers.set(dest.strip(','), src_value)

    # add 명령어 처리
    def handle_add(self, instruction):
        _, src1, src2, dest = instruction.split()
        self.registers.set(dest.strip(','), self.registers.get(src1.strip(',')) + self.registers.get(src2.strip(',')))

    # save 명령어 처리
    def handle_save(self, instruction):
        _, src, offset, dest = instruction.split()
        self.save_register_state(int(offset.strip(',')))

    # ret 명령어 처리
    def handle_ret(self, instruction):
        if self.call_stack:
            return_address = self.registers.get('%i7')
            self.program_counter = return_address
            print(f"PC 복구: {self.program_counter}")
        else:
            print("No return address found, ready for ending program.")

    # restore 명령어 처리
    def handle_restore(self, instruction):
        # restore가 추가적인 인자를 가질 떄 restore a, b, c -> c = a+b 연산 수행 후 복구
        if instruction != "restore":
            regs = [reg.strip(',') for reg in instruction.split()[1:]]
            self.registers.set(regs[2], self.registers.get(regs[0]) + self.registers.get(regs[1]))

        self.memory.write(self.registers.get('%sp'), 0)
        self.registers.set('%sp', self.registers.get('%fp'))
        if self.memory.read(self.registers.get('%fp')) == 0:
            self.registers.set('%fp', self.memory.__sizeof__() - 1)
        else:
            self.registers.set('%fp', self.memory.read(self.registers.get('%fp')))

    # call 명령어 처리
    def handle_call(self, instruction):
        _, label_name = instruction.split()
        return_address = self.program_counter + 1  # 다음 명령어 주소를 반환 주소로 설정
        self.call_stack.append(return_address)  # 반환 주소를 호출 스택에 추가
        self.registers.set('%i7', return_address)  # %i7 레지스터에도 저장

        if label_name in self.instructions:
            print(f"****************** label - <{label_name}> call******************")
            self.execute(label_name)
            self.program_counter = self.call_stack.pop() - 1  # 호출이 끝나면 반환 주소로 복귀
            print(f"******************label - <{label_name}> return******************")
        else:
            raise ValueError(f"함수 {label_name}을(를) 찾을 수 없습니다.")

    # 메모리 주소 해석
    def parse_address(self, mem_addr):
        base_reg, offset = mem_addr.strip('[],').split('+-')
        return self.registers.get(base_reg) - int(offset)

    # 스택 프레임 저장
    def save_register_state(self, offset_value):
        sp_value = self.registers.get('%sp')
        new_sp = sp_value + offset_value
        if new_sp < 0:
            raise ValueError("스택 포인터가 음수입니다.")
        self.memory.write(new_sp, self.registers.get('%sp'))
        self.registers.set('%fp', sp_value)
        self.registers.set('%sp', new_sp)