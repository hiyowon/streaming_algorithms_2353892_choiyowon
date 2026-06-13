# Streaming Algorithms on MovieLens 1M
# Student: 2353892, choiyowon
# Algorithms: Bloom Filter, Count-Min Sketch

import random
import time
from collections import defaultdict

RATINGS_PATH = "ratings.dat"
MASK = (1 << 64) - 1
CONST = 0x9e3779b97f4a7c15


def mix64(x: int) -> int:
    x &= MASK
    x ^= x >> 33
    x = (x * 0xff51afd7ed558ccd) & MASK
    x ^= x >> 33
    x = (x * 0xc4ceb9fe1a85ec53) & MASK
    x ^= x >> 33
    return x & MASK


class BloomFilter:
    def __init__(self, m_bits: int, k_hashes: int):
        self.m_bits = m_bits
        self.k_hashes = k_hashes
        self.bits = bytearray((m_bits + 7) // 8)

    def _hashes(self, key: int):
        h1 = mix64(key)
        h2 = mix64(key ^ CONST) | 1
        for i in range(self.k_hashes):
            yield (h1 + i * h2 + i * i * CONST) % self.m_bits

    def add(self, key: int):
        for h in self._hashes(key):
            self.bits[h >> 3] |= 1 << (h & 7)

    def contains(self, key: int) -> bool:
        for h in self._hashes(key):
            if not (self.bits[h >> 3] & (1 << (h & 7))):
                return False
        return True

    def memory_bytes(self) -> int:
        return len(self.bits)


class CountMinSketch:
    def __init__(self, width: int, depth: int):
        self.width = width
        self.depth = depth
        self.table = [[0] * width for _ in range(depth)]
        self.seeds = [(CONST * (i + 1)) & MASK for i in range(depth)]

    def _hash(self, item: int, row: int) -> int:
        return mix64(item ^ self.seeds[row]) % self.width

    def add(self, item: int, count: int = 1):
        for row in range(self.depth):
            self.table[row][self._hash(item, row)] += count

    def estimate(self, item: int) -> int:
        return min(self.table[row][self._hash(item, row)] for row in range(self.depth))

    def memory_bytes(self) -> int:
        # Each counter is treated as 32-bit unsigned integer in the report.
        return self.width * self.depth * 4


def iter_rating_events(path=RATINGS_PATH):
    """MovieLens 1M ratings.dat: UserID::MovieID::Rating::Timestamp"""
    with open(path, "r", encoding="latin-1") as f:
        for line in f:
            user_id, movie_id, rating, timestamp = line.rstrip("\n").split("::")
            yield int(user_id), int(movie_id), int(rating), int(timestamp)


def pair_key(user_id: int, movie_id: int) -> int:
    # MovieLens 1M movie id is below 10000, so this key is collision-free here.
    return user_id * 10000 + movie_id


def build_ground_truth(path=RATINGS_PATH):
    true_pairs = set()
    movie_freq = defaultdict(int)
    n = 0
    for user_id, movie_id, rating, timestamp in iter_rating_events(path):
        true_pairs.add(pair_key(user_id, movie_id))
        movie_freq[movie_id] += 1
        n += 1
    return n, true_pairs, movie_freq


def run_bloom_filter(path=RATINGS_PATH, m_bits=10_000_000, k_hashes=7):
    bf = BloomFilter(m_bits, k_hashes)
    start = time.perf_counter()
    for user_id, movie_id, rating, timestamp in iter_rating_events(path):
        bf.add(pair_key(user_id, movie_id))
    elapsed = time.perf_counter() - start
    return bf, elapsed


def run_count_min_sketch(path=RATINGS_PATH, width=5000, depth=7):
    cms = CountMinSketch(width, depth)
    start = time.perf_counter()
    for user_id, movie_id, rating, timestamp in iter_rating_events(path):
        cms.add(movie_id)
    elapsed = time.perf_counter() - start
    return cms, elapsed


if __name__ == "__main__":
    random.seed(20260612)
    n, true_pairs, movie_freq = build_ground_truth()
    bf, bf_time = run_bloom_filter()
    cms, cms_time = run_count_min_sketch()

    print("records:", n)
    print("Bloom Filter memory(bytes):", bf.memory_bytes(), "time:", bf_time)
    print("Count-Min Sketch memory(bytes):", cms.memory_bytes(), "time:", cms_time)

    # Example ground-truth comparison for Count-Min Sketch
    errors = []
    for movie_id, true_count in movie_freq.items():
        est = cms.estimate(movie_id)
        errors.append(est - true_count)
    print("CMS mean absolute error:", sum(abs(e) for e in errors) / len(errors))
