class Cache:
    def __init__(self, memory, cache_size=16):
        self.cache_size = cache_size
        self.cache = [-1] * cache_size  # Simple direct-mapped cache
        self.memory = memory  # 연결된 메모리 인스턴스

    def access(self, address):
        index = address % self.cache_size
        if self.cache[index] != address:  # 캐시 미스
            print(f"Cache miss at index {index} for address {address}. Reloading from memory.")
            print(self.cache)
            self.cache[index] = address  # 메모리에서 주소 로드
            return self.memory.read(address)
        print(f"Cache hit at index {index} for address {address}.")
        print(self.cache)
        return self.memory.read(address)

    def __repr__(self):
        return str(self.cache)  # 배열 형태로 메모리 출력