"""Offline checks for password hashing. No network, no database writes, no model calls.

Run from the project root:  .venv/bin/python tests/test_auth.py

The point of this file is the fourth check: signup and login must use the same function,
the same salt handling and the same iteration count. If they ever drift apart, a correct
password stops matching and the test fails loudly instead of users being locked out.
"""
import hashlib
import hmac
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.auth import ALGORITHM, ITERATIONS, hash_password, verify_password

failures = []


def check(name: str, condition: bool) -> None:
    print(f"  {'PASS' if condition else 'FAIL'}  {name}")
    if not condition:
        failures.append(name)


print("Stored format")
record = hash_password("correct horse battery staple")
algorithm, salt, digest = record.split("$")
check("three $-separated fields", len(record.split("$")) == 3)
check(f"algorithm is {ALGORITHM}", algorithm == ALGORITHM)
check("digest is 64 hex characters", len(digest) == 64)
check("salt is non-empty", len(salt) > 0)

print("\nRound trip")
check("correct password verifies", verify_password("correct horse battery staple", record))
check("wrong password rejected", not verify_password("wrong password", record))
check("empty password rejected", not verify_password("", record))

print("\nSalt handling")
first = hash_password("same password")
second = hash_password("same password")
check("two hashes of one password differ", first != second)
check("salts differ", first.split("$")[1] != second.split("$")[1])
check("both still verify", verify_password("same password", first) and verify_password("same password", second))

print("\nSignup and login agree (the one that must never break)")
# Recompute the digest independently, the way login does: take the salt out of the
# middle of the stored string and re-derive with the documented settings.
_, stored_salt, stored_digest = record.split("$")
recomputed = hashlib.pbkdf2_hmac(
    "sha256", "correct horse battery staple".encode("utf-8"), stored_salt.encode("utf-8"), ITERATIONS
).hex()
check(f"iteration count is {ITERATIONS:,}", ITERATIONS == 120_000)
check("independent re-derivation matches the stored digest", hmac.compare_digest(recomputed, stored_digest))

print("\nMalformed records fail closed rather than raising")
for bad in ["", "not-a-hash", "pbkdf2_sha256$onlytwo", "argon2$salt$digest", "pbkdf2_sha256$$", "a$b$c$d"]:
    check(f"rejects {bad!r}", verify_password("anything", bad) is False)

print("\nThe seeded format from the supplied database")
# Shape only — no real hash, salt or password from the database appears in this file.
seeded = f"{ALGORITHM}$seedsalt123$" + hashlib.pbkdf2_hmac(
    "sha256", b"password", b"seedsalt123", ITERATIONS
).hex()
check("a seeded-style record verifies with the same code path", verify_password("password", seeded))

print()
if failures:
    print(f"{len(failures)} check(s) failed: {failures}")
    sys.exit(1)
print("All checks passed.")
