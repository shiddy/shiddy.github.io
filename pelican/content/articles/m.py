import time

print("enabling mouse input...")
try:
    print("\033[?1000l")
    for _ in range(200):
        time.sleep(0.01)
finally:
    print("\033[?1000h")
    print("mouse input diabled")
