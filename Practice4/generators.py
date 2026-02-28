def squares_up_to(n):
    for i in range(n + 1):
        yield i * i


def even_numbers(n):
    for i in range(0, n + 1):
        if i % 2 == 0:
            yield i


def divisible_by_3_and_4(n):
    for i in range(0, n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i


def squares(a, b):
    for i in range(a, b + 1):
        yield i * i


def countdown(n):
    while n >= 0:
        yield n
        n -= 1


if __name__ == "__main__":
    print(list(squares_up_to(5)))
    print(",".join(map(str, even_numbers(10))))
    print(list(divisible_by_3_and_4(50)))
    print(list(squares(1, 5)))
    print(list(countdown(5)))
