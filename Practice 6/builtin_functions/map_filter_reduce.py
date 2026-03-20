from functools import reduce


numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

squared_numbers = list(map(lambda x: x**2, numbers))
print(f"Original: {numbers}")
print(f"Squared:  {squared_numbers}")

even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
print(f"Even numbers only: {even_numbers}")

product = reduce(lambda x, y: x * y, [1, 2, 3, 4, 5])
print(f"Product of [1, 2, 3, 4, 5] using reduce: {product}")