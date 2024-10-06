class SPARCSimulator:
    def __init__(self):
        # 메모리 초기화 (256 바이트)
        self.memory = [1] * 256

        # 레지스터 초기화 
        self.init_register()

        # 프로그램 카운터 초기화
        self.program_counter = 0

        # 어셈블리 명령어를 저장할 딕셔너리
        self.instructions = {}

    def init_register(self):
        # 일반 레지스터
        self.registers = {f"%g{i}": 0 for i in range(8)}  # %g0 - %g7 (전역 레지스터)
        self.registers.update({f"%o{i}": 0 for i in range(8)})  # %o0 - %o7 (출력 레지스터), %i7은 리턴 주소
        self.registers.update({f"%l{i}": 0 for i in range(8)})  # %l0 - %l7 (지역 레지스터)
        self.registers.update({f"%i{i}": 0 for i in range(8)})  # %i0 - %i7 (입력 레지스터)

        # 특수 레지스터
        self.registers['%sp'] = 0  # 스택 포인터
        self.registers['%fp'] = 0  # 프레임 포인터

        self.set_register_value('%sp', len(self.memory) - 1) # 스택 포인터 초기화 (메모리 맨 끝에서 스택 시작)
        self.set_register_value('%fp', self.get_register_value('%sp'))

    # .S에서 명령어를 읽어 프로그램에 로드
    def load_program_from_file(self, file_path):

        try:
            with open(file_path, 'r') as f:
                asm_code = f.readlines()

            current_label = None
            for line in asm_code:
                # 주석 제거
                line = line.split('!')[0].strip()
                # 메타데이터 무시
                if line.startswith('.'):
                    continue
                # 빈 줄 무시
                if not line:
                    continue

                # 라벨 확인
                if ':' in line:
                    current_label = line.replace(':', '').strip()  # ':' 제거
                    self.instructions[current_label] = []
                elif current_label:
                    self.instructions[current_label].append(line)

        except FileNotFoundError:
            print(f"파일을 찾을 수 없습니다: {file_path}")
        except IOError:
            print(f"파일을 읽는 중 오류가 발생했습니다: {file_path}")

    # 주어진 라벨의 명령어를 순차적으로 실행
    def execute(self, label='main', debug=False):
        if label not in self.instructions:
            raise ValueError(f"라벨 '{label}'을(를) 찾을 수 없습니다.")

        self.program_counter = 0  # 해당 라벨에서 시작하는 프로그램 카운터
        instructions = self.instructions[label]  # 해당 라벨의 명령어 리스트 가져오기

        print(f"instructions: {instructions}")
        print("*****************************", label)
        while self.program_counter < len(instructions):
            instruction = instructions[self.program_counter]

            if debug:
                print(f"현재 실행중인 명령어: \"{instruction}\"")

            # ret 명령어 처리
            if instruction.startswith("ret"):
                self.handle_ret()
                break

            # 명령어 처리
            self.handle_instruction(instruction)
            # 프로그램 카운터 증가
            self.program_counter += 1

            print("#Debugging -------------------")
            print(self.list_registers())  # 지우기
            print(self.memory)  # 지우기
            print(self.program_counter)
            print(self.get_register_value('%sp'))
            print(self.get_register_value('%fp'))
            print("#-----------------------------")

    # 어셈블리 명령어를 특정 핸들러로 보냄
    def handle_instruction(self, instruction):
        instruction = instruction.split("!")[0].strip()  # 주석 제거
        if instruction == "" or ":" in instruction:
            return  # 빈 라인 및 라벨 무시

        handlers = {
            "save": self.handle_save,
            "mov": self.handle_mov,
            "st": self.handle_st,
            "ld": self.handle_ld,
            "add": self.handle_add,
            "restore": self.handle_restore,
            "call": self.handle_call,
            "jmp": self.handle_jmp
        }

        for key, handler in handlers.items():
            if instruction.startswith(key):
                handler(instruction)
                break

    # save 명령어 처리 (현재 레지스터 상태를 스택에 저장하고 새로운 스택 프레임 생성)
    def handle_save(self, instruction):
        _, src, offset, dest = instruction.split()

        # 쉼표 제거 및 int로 변환
        offset_value = int(offset.strip(','))

        # 현재 프레임 포인터 %fp를 %sp로 복사하고 스택 포인터를 조정
        sp_value = self.get_register_value('%sp')
        new_sp = sp_value + offset_value

        # %sp와 %fp 값을 조정하여 스택을 설정
        self.set_register_value('%fp', sp_value)  # 현재 %sp 값을 %fp에 저장
        self.set_register_value('%sp', new_sp)  # %sp에 오프셋 값을 더해 새로운 스택 프레임 설정

    # mov 명령어 처리
    def handle_mov(self, instruction):
        _, src, dest = instruction.split()
        if src.strip(',').isdigit():
            src_value = int(src.strip(','))
        else:
            src_value = self.get_register_value(src.strip(','))
        self.set_register_value(dest.strip(','), src_value)

    # st 명령어 처리 (레지스터 값을 메모리에 저장)
    def handle_st(self, instruction):
        _, src, mem_addr = instruction.split()
        addr = self.get_memory_address(mem_addr)
        self.memory[addr] = self.get_register_value(src.strip(','))

    # ld 명령어 처리 (메모리 값을 레지스터로 로드)
    def handle_ld(self, instruction):
        _, mem_addr, dest = instruction.split()
        addr = self.get_memory_address(mem_addr)
        self.set_register_value(dest.strip(','), self.memory[addr])

    # add 명령어 처리
    def handle_add(self, instruction):
        _, src1, src2, dest = instruction.split()
        val1 = self.get_register_value(src1.strip(','))
        val2 = self.get_register_value(src2.strip(','))
        self.set_register_value(dest.strip(','), val1 + val2)

    # jmp 명령어 처리 (즉시 분기)
    def handle_jmp(self, instruction):
        print(f"Executing: {instruction}")
        _, target_label = instruction.split()
        self.program_counter = self.find_label(target_label)

    # restore 명령어 처리 (프레임 복구)
    def handle_restore(self):
        # %fp 값을 %sp로 복원하여 이전 스택 상태 복원
        self.set_register_value('%sp', self.get_register_value('%fp'))

    # ret 명령어 처리 (함수 반환)
    def handle_ret(self):
        print(f"Executing: ret")
        # %i7 레지스터에 저장된 리턴 주소로 복귀
        return_address = self.get_register_value('%i7')
        if return_address == 0:  # 프로그램 종료 시점
            print("프로그램 종료")
        else:
            # 이전 명령어로 돌아가서 실행을 재개
            self.program_counter = return_address - 1  # 돌아온 주소에서 계속 실행

    # call 명령어 처리 (함수 호출)
    def handle_call(self, instruction):
        _, label_name = instruction.split()

        # 현재 프로그램 카운터 값 + 1을 %i7 (리턴 주소)에 저장
        self.set_register_value('%i7', self.program_counter + 1)

        # 라벨이 존재하는지 확인
        if self.find_label(label_name):
            # 해당 라벨을 실행
            self.execute(label_name, True)
        else:
            raise ValueError(f"함수 {label_name}을(를) 찾을 수 없습니다.")

    # 해당 instruction set에서 특정 label이 존재하는 찾기
    def find_label(self, label_name):
        if label_name in self.instructions:
            print(f"find_label({label_name}) 결과 라벨 {label_name}은 존재합니다.")
            return True
        else:
            print(f"find_label({label_name}) 결과 라벨 {label_name}은 존재하지 않습니다.")
            return False;

    # 레지스터 값을 반환
    def get_register_value(self, reg):
        reg = reg.strip(',')  # 쉼표 제거
        if reg not in self.registers:
            raise KeyError(f"잘못된 레지스터: {reg}")
        return self.registers[reg]

    # 레지스터에 값을 설정
    def set_register_value(self, reg, value):
        reg = reg.strip(',')  # 쉼표 제거
        if reg not in self.registers:
            raise KeyError(f"잘못된 레지스터: {reg}")
        self.registers[reg] = value

    # 메모리 주소를 해석
    def get_memory_address(self, mem_addr):
        if mem_addr.endswith(','):
            mem_addr = mem_addr[:-1]
        if not (mem_addr.startswith('[') and mem_addr.endswith(']')):
            raise ValueError(f"잘못된 메모리 주소: {mem_addr}")

        # 대괄호 안의 내용 추출
        inner_content = mem_addr[1:-1].strip()  # 예: "%fp+-4"

        # %fp 확인
        if not inner_content.startswith('%fp'):
            raise ValueError(f"잘못된 메모리 주소: {mem_addr}")

        # %fp 이후의 문자열을 분리
        remaining = inner_content[3:].strip()  # 예: "+-4" 또는 "-4"

        # 부호 처리
        sign = None
        if remaining.startswith('+-'):
            sign = '-'  # '+-'는 음수로 해석
            remaining = remaining[2:].strip()  # '+-'를 제외한 나머지 부분
        elif remaining.startswith('+'):
            sign = '+'
            remaining = remaining[1:].strip()  # +를 제외한 나머지 부분
        elif remaining.startswith('-'):
            sign = '-'
            remaining = remaining[1:].strip()  # -를 제외한 나머지 부분
        else:
            raise ValueError(f"잘못된 메모리 주소: {mem_addr}")

        # 남은 문자열이 숫자인지 확인
        if not remaining.isdigit():
            raise ValueError(f"잘못된 메모리 주소: {mem_addr}")

        # 부호와 숫자를 결합하여 오프셋 값 계산
        offset_value = int(f"{sign}{remaining}")

        # 메모리 주소 반환
        return self.get_register_value('%fp') + offset_value

    # 레지스터와 값 포함 리스트
    def list_registers(self):
        reg_list = []
        for reg, value in self.registers.items():
            reg_list.append(f"{reg}: {value}")
        return reg_list

if __name__ == "__main__":
    simulator = SPARCSimulator()
    simulator.load_program_from_file("asm/test.s")
    simulator.execute("main",True)
