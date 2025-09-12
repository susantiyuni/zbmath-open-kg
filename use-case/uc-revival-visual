import pandas as pd
import matplotlib.pyplot as plt

# Input data
data = [
("03",1860,4),("03",1870,81),("03",1880,98),("03",1890,9),("03",1900,17),
("03",1910,18),("03",1920,49),("03",1930,303),("03",1940,142),("03",1950,441),
("03",1960,1998),("03",1970,12939),("03",1980,16683),("03",1990,20779),("03",2000,27657),
("03",2010,25419),("03",2020,5290),
("60",1760,2),("60",1840,1),("60",1860,3),("60",1870,120),("60",1880,194),
("60",1890,65),("60",1900,19),("60",1910,12),("60",1920,17),("60",1930,128),
("60",1940,68),("60",1950,297),("60",1960,2053),("60",1970,22103),("60",1980,34287),
("60",1990,37365),("60",2000,45390),("60",2010,49527),("60",2020,13743)
]

df = pd.DataFrame(data, columns=["prefix","decade","count"])

# Create total per decade for normalization
decade_totals = df.groupby("decade")["count"].sum().reset_index().rename(columns={"count":"total"})
df = df.merge(decade_totals, on="decade")
df["normalized"] = df["count"] / df["total"] * 100

# Absolute counts plot (log scale)
plt.figure(figsize=(10,6))
for prefix, group in df.groupby("prefix"):
    plt.plot(group["decade"], group["count"], marker="o", label=f"MSC {prefix}")
plt.yscale("log")
plt.xlabel("Decade")
plt.ylabel("Publications (log scale)")
plt.title("Absolute publication counts per decade (MSC 03=Logic, 60=Probability)")
plt.legend()
plt.grid(True, which="both", linestyle="--", alpha=0.5)
plt.show()

# Normalized share plot
plt.figure(figsize=(10,6))
for prefix, group in df.groupby("prefix"):
    plt.plot(group["decade"], group["normalized"], marker="o", label=f"MSC {prefix}")
plt.xlabel("Decade")
plt.ylabel("Share of publications (%)")
plt.title("Relative share of publications per decade (MSC 03=Logic, 60=Probability)")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
plt.show()
