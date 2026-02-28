import json

with open("sample-data.json") as f:
    data = json.load(f)

print("Interface Status")
print("=" * 80)
print(f"{'DN':50} {'Description':20} {'Speed':8} {'MTU':6}")
print("-" * 80)

for item in data["imdata"]:
    attrs = item["l1PhysIf"]["attributes"]
    dn = attrs["dn"]
    descr = attrs["descr"]
    speed = attrs["speed"]
    mtu = attrs["mtu"]

    print(f"{dn:50} {descr:20} {speed:8} {mtu:6}")
