import re

with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

prices = re.findall(r"\d[\d\s]*,\d{2}", text)

products = re.findall(r"\d+\.\n(.+)", text)

total = re.search(r"ИТОГО:\s*\n?([\d\s]+,\d{2})", text)

datetime = re.search(r"\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2}:\d{2}", text)

payment = re.search(r"(Банковская карта|Наличные)", text)

print("Products:")
for p in products:
    print("-", p)

print("\nPrices:")
for p in prices:
    print(p)

if total:
    print("\nTotal:", total.group(1))

if datetime:
    print("DateTime:", datetime.group())

if payment:
    print("Payment method:", payment.group())