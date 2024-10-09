class CacheBlock:
    def __init__(self):
        self.valid = False  # 블록이 유효한지 여부
        self.tag = None  # 블록의 태그
        self.data = None  # 블록에 저장된 데이터
        self.dirty = False  # 더티 비트 (쓰기 연산 후 True로 설정)


class CacheSet:
    def __init__(self, n):
        self.blocks = [CacheBlock() for _ in range(n)]  # N-way set associative 캐시 블록들

    # 태그에 해당하는 블록을 찾아 반환, 없으면 None 반환
    def find_block(self, tag):
        for block in self.blocks:
            if block.valid and block.tag == tag:
                return block
        return None

    # 비어있는 블록을 찾아 반환
    def find_empty_block(self):
        for block in self.blocks:
            if not block.valid:
                return block
        return None

    # victim 블록 찾기 (무작위, LRU 등 알고리즘 개선 필요)
    def find_victim_block(self):
        # 첫 번째 블록을 교체 대상으로 설정
        return self.blocks[0]

    # cache set 에서 빈 블록(또는 교체 블록) 찾아 값 교체 하기
    def replace_block(self, tag, data, cache):

        # 해당 set 에서 빈 블록 찾기
        block = self.find_empty_block()

        # 해당 set 에서 빈 블록이 없는 경우 victim 찾기
        if block is None:
            block = self.find_victim_block()

            # 기존 블록이 dirty면 메모리에 반영 (write-back 방식)
            if block.dirty:
                print(f"Writing back dirty block to memory: Tag {block.tag}, Data {block.data}")
                cache.memory.write(block.tag, block.data)

        block.valid = True
        block.tag = tag
        block.data = data
        block.dirty = False  # 새로 저장된 데이터이므로 더티 비트 초기화
        return block


class Cache:
    def __init__(self, memory, cache_size, block_size, n_way=1):
        self.memory = memory  # 메모리 객체
        self.cache_size = cache_size  # 캐시 크기
        self.block_size = block_size  # 블록 크기
        self.n_way = n_way  # n-way 세트 연관 방식
        self.num_sets = cache_size // (block_size * n_way)  # 캐시 내의 세트 수 계산
        self.sets = [CacheSet(n_way) for _ in range(self.num_sets)]  # 세트 배열 초기화

    # 캐시에서 데이터를 찾고, 없으면 메모리에서 로드
    def access_cache(self, address):
        # 주소에서 태그와 인덱스 추출
        index = (address // self.block_size) % self.num_sets
        tag = address // (self.block_size * self.num_sets)

        # 해당 세트에서 태그에 맞는 블록을 찾음
        cache_set = self.sets[index]
        block = cache_set.find_block(tag)

        if block:
            print(f"Cache hit: {block.data}")
            return block.data
        else:
            print("Cache miss")
            # 캐시 미스일 때 메모리에서 로드하고 캐시에 저장
            data = self.load_from_memory(address)
            cache_set.replace_block(tag, data, self)
            return data

    # 메모리에서 데이터를 로드하는 함수
    def load_from_memory(self, address):
        print(f"Loading data from memory for address {address}")
        data = self.memory.read(address)
        return data

    # 캐시 블록에 데이터를 씀 (write-back 방식으로 캐시에만 저장)
    def write_cache(self, address, data):
        # 주소에서 태그와 인덱스 추출
        index = (address // self.block_size) % self.num_sets
        tag = address // (self.block_size * self.num_sets)

        # 해당 세트에서 태그에 맞는 블록을 찾음
        cache_set = self.sets[index]
        block = cache_set.find_block(tag)

        if block:
            print(f"Writing data to cache block: {data}")
            block.data = data
            block.dirty = True  # 캐시에 데이터가 쓰였으므로 더티 비트 설정
        else:
            print("Cache miss during write. Loading from memory and writing to cache.")
            cache_set.replace_block(tag, data, self)

    # 캐시의 각 세트와 그 세트 안의 블록들을 출력
    def __repr__(self):
        cache_repr = []
        for set_index, cache_set in enumerate(self.sets):
            set_repr = [f"Set {set_index}:"]  # 각 세트의 인덱스
            for block_index, block in enumerate(cache_set.blocks):
                set_repr.append(
                    f"  Block {block_index}: Tag: {block.tag}, Valid: {block.valid}, Dirty: {block.dirty}, Data: {block.data}"
                )
            cache_repr.append('\n'.join(set_repr))
        return '\n'.join(cache_repr)

    # 캐시의 모든 dirty 블록을 메모리에 반영
    def flush_cache(self):
        for cache_set in self.sets:
            for block in cache_set.blocks:
                if block.valid and block.dirty:
                    print(f"Flushing block with Tag {block.tag} to memory: Data {block.data}")
                    self.memory.write(block.tag, block.data)  # 메모리에 반영
                    block.dirty = False  # 메모리에 반영 후 dirty 비트 초기화

    # 캐시의 모든 블록을 초기화
    def clear_cache(self):
        for cache_set in self.sets:
            for block in cache_set.blocks:
                block.valid = False
                block.tag = None
                block.data = None
                block.dirty = False
        print("Cache cleared and initialized.")
