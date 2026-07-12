# q10.py  — deterministic miner
import hashlib

TOKEN = "048a21182d0d7a71"
DIFFICULTY = 26          # PASTE your required leading-zero BITS

def leading_zero_bits(digest: bytes) -> int:
    bits = 0
    for byte in digest:
        if byte == 0:
            bits += 8
            continue
        # count leading zeros in this byte
        bits += 8 - byte.bit_length()
        break
    return bits

nonce = 0
while True:
    d = hashlib.sha256(f"{TOKEN}:{nonce}".encode()).digest()
    if leading_zero_bits(d) >= DIFFICULTY:
        print("NONCE =", nonce)
        break
    nonce += 1