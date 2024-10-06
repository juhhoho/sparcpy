class CacheLine:
    def __init__(self):
        self.valid = False  # 유효 비트
        self.dirty = False  # 더티 비트
        self.tag = None  # 태그
        self.data = [0] * 4  # 4바이트 데이터 (예: 32비트 단어)


class Cache:
    def __init__(self, memory, cache_size=16):
        self.cache_size = cache_size
        self.cache = [CacheLine() for _ in range(cache_size)]  # 캐시 라인 배열 생성
        self.memory = memory  # 연결된 메모리 인스턴스

    def access(self, address):
        # block index, tag 정의
        index = address % self.cache_size
        tag = address // self.cache_size
        print(f"index: {index}, tag: {tag}")

        # 캐시 라인 검색
        cache_line = self.cache[index]

        # 캐시 히트 검사
        if cache_line.valid and cache_line.tag == tag:
            print(f"Cache hit at index {index}/{int(self.memory.__sizeof__() / self.cache_size)} for address {address}.")
            return cache_line.data

        # 캐시 미스 처리
        print(f"Cache miss at index {index}/{int(self.memory.__sizeof__() / self.cache_size)} for address {address}.\nReloading from memory.")

        # 데이터 리로드
        self.load_from_memory(address, cache_line)

        return cache_line.data


    def load_from_memory(self, address, cache_line):
        # 메모리에서 데이터 로드
        # 현재 주소가 비트플립이 발생했다고 가정하여 비트 단위로 리로드
        data_from_memory = self.memory.read(address)
        print(f"Data loaded from memory: {data_from_memory}")

        # 데이터를 1바이트 단위로 캐시에 저장 (비트 플립 발생 시)
        for i in range(4):
            cache_line.data[i] = (data_from_memory >> (i * 8)) & 0xFF  # 각 바이트 저장

        # 캐시 라인 업데이트
        cache_line.valid = True
        cache_line.dirty = False  # 새로 로드했으므로 dirty bit는 False
        cache_line.tag = address // self.cache_size  # 태그 업데이트

    def write(self, address, value):
        # block index, tag 정의
        index = address % self.cache_size
        tag = address // self.cache_size
        print(f"index: {index}, tag: {tag}")

        # 캐시 라인 검색
        cache_line = self.cache[index]

        # 캐시 히트 검사
        if cache_line.valid and cache_line.tag == tag:
            print(f"Cache hit at index {index}/{int(self.memory.__sizeof__() / self.cache_size)} for address {address}.\nWriting value {value} to cache.")
            # 캐시에 값 저장 및 더티 비트 설정
            self.update_cache_line(cache_line, address, value)
        else:
            # 캐시 미스일 경우, 메모리에서 먼저 데이터를 로드한 후 캐시 업데이트
            print(
                f"Cache miss at index {index}/{int(self.memory.__sizeof__() / self.cache_size)} for address {address}.\nReloading from memory and writing value {value}.")
            self.load_from_memory(address, cache_line)
            self.update_cache_line(cache_line, address, value)

    def update_cache_line(self, cache_line, address, value):
        # 데이터를 1바이트 단위로 저장 (value는 32비트 정수로 가정)
        for i in range(4):
            cache_line.data[i] = (value >> (i * 8)) & 0xFF  # 각 바이트 저장

        # 캐시 라인 업데이트
        cache_line.valid = True
        cache_line.dirty = True  # 쓰기 작업이므로 더티 비트를 설정
        cache_line.tag = address // self.cache_size  # 태그 업데이트

    def __repr__(self):
        # 캐시의 모든 라인 출력
        return '\n'.join(
            [f"Block Index {i}: {line.data}, Valid: {line.valid}, Dirty: {line.dirty}, Tag: {line.tag}" for i, line in
             enumerate(self.cache)]
        )






