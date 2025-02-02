import os
import math
import random
import time
import QuantumRingsLib
from QuantumRingsLib import QuantumRegister, ClassicalRegister, QuantumCircuit
from QuantumRingsLib import QuantumRingsProvider
from QuantumRingsLib import job_monitor
from sympy import nextprime, isprime

# API Bağlantısını Kur
api_token = "rings-200.LZDUM79WHwVBdR1Z0WDNwibRwokIqVT9"
account_name = "aslihanzehradonmez@gmail.com"

provider = QuantumRingsProvider(token=api_token, name=account_name)
backend = provider.get_backend("scarlet_quantum_rings")
shots = 1024

def grover_oracle(qc, n):
    qc.h(range(n))
    qc.z(n-1)
    qc.h(range(n))
    return qc

def diffusion_operator(qc, n):
    qc.h(range(n))
    qc.x(range(n))
    
    if n > 1:
        qc.h(n-1)
        try:
            qc.mcx(list(range(n-1)), n-1)
        except Exception:
            if n >= 3:
                qc.ccx(n-3, n-2, n-1)
            elif n == 2:
                qc.cx(n-2, n-1)
        qc.h(n-1)
    
    qc.x(range(n))
    qc.h(range(n))
    return qc

def classical_factorization(N):
    """Hızlı klasik algoritmalar ile çarpanları bulmaya çalış."""
    for i in range(2, min(10**6, int(math.sqrt(N)) + 1)):
        if N % i == 0:
            return i, N // i
    return None

def quantum_factorization(N, n):
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    
    grover_oracle(qc, n)
    diffusion_operator(qc, n)
    
    num_iterations = max(1, int(math.pi / 4 * math.sqrt(2**n)))
    for _ in range(num_iterations):
        grover_oracle(qc, n)
        diffusion_operator(qc, n)
    
    qc.measure(range(n), range(n))
    
    print("QuantumRingsLib üzerinde çalıştırılıyor...")
    job = backend.run_quantum_task(qc)
    results = job.get_result()
    
    counts = results.get_counts()
    most_common = max(counts, key=counts.get)
    factor_guess = int(most_common, 2)
    
    if N % factor_guess == 0:
        return factor_guess, N // factor_guess
    else:
        return None

# 128 qubit kullan
n = 128

# İki büyük asal sayı seçerek yarı asal bir N üret
p = nextprime(random.randint(2*(n//2 - 1), 2*(n//2)))
q = nextprime(random.randint(2*(n//2 - 1), 2*(n//2)))
N = p * q

print(f"Çarpanlarını bulmaya çalıştığımız yarı asal sayı: {N} (n = {n})")

# Önce klasik faktorizasyon dene
start = time.time()
classic_result = classical_factorization(N)
if classic_result:
    end = time.time()
    print(f"(Klasik) Bulunan çarpanlar: {classic_result}")
    print(f"Toplam süre: {end - start} saniye")
else:
    print("Klasik algoritma başarısız, kuantum kullanılıyor...")
    result = quantum_factorization(N, n)
    end = time.time()
    if result:
        print(f"(Kuantum) Bulunan çarpanlar: {result}")
    else:
        print("Çözüm bulunamadı, farklı bir yaklaşım deneyin!")
    print(f"Toplam süre: {end - start} saniye")