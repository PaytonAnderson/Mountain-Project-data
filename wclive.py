import sys

count = 0

for line in sys.stdin:
    count += 1
    if count % 100_000 == 0:
        print(f'\r{count}', end='')

print(f'\r{count}')
