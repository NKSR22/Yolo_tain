import time

# Fill in the measured average inference time (ms) for each setup after running Lab 7 and Lab 8
cpu_ms = float(input("CPU-only avg inference time (ms) from Lab 7: ") or 0)
hailo_ms = float(input("AI HAT (Hailo) avg inference time (ms): ") or 0)

if cpu_ms and hailo_ms:
    speedup = cpu_ms / hailo_ms
    print(f"CPU: {cpu_ms:.1f} ms | AI HAT: {hailo_ms:.1f} ms | Speedup: {speedup:.1f}x")
