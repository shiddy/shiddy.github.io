print('Forground')
print("Standard Colors")
for i in range(0, 8):
    print(f"\033[38;5;{i}m##\033[0m", end='')
print('')

print("High Intensity Colors")
for i in range(8, 16):
    print(f"\033[38;5;{i}m##\033[0m", end='')
print('')

print("216 Colors")
for i in range(16, 232):
    print(f"\033[38;5;{i}m#\033[0m", end='')
    if (i-15) % 36 == 0:
        print('')

print("Grayscale Colors")
for i in range(232, 255):
    print(f"\033[38;5;{i}m#\033[0m", end='')
print('')

print('Background')
print("Standard Colors")
for i in range(0, 8):
    print(f"\033[48;5;{i}m  \033[0m", end='')
print('')

print("High Intensity Colors")
for i in range(8, 16):
    print(f"\033[48;5;{i}m  \033[0m", end='')
print('')

print("216 Colors")
for i in range(16, 232):
    print(f"\033[48;5;{i}m \033[0m", end='')
    if (i-15) % 36 == 0:
        print('')

print("Grayscale Colors")
for i in range(232, 255):
    print(f"\033[48;5;{i}m \033[0m", end='')
print('')

def rgb_to_8bit(r, g, b):
    return int(16 + 36 * (r / 51) + 6 * (g / 51) + (b / 51))

print('Can I make some red with rgb?')
print(f"\033[48;5;{rgb_to_8bit(255, 0, 0)}m       \033[0m")

print('What about purple?')
print(f"\033[48;5;{rgb_to_8bit(100, 0, 200)}m       \033[0m")
