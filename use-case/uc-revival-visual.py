import pandas as pd
import matplotlib.pyplot as plt

# Data from user
data = [
    ("03", 1860, 4), ("03", 1870, 81), ("03", 1880, 98), ("03", 1890, 9),
    ("03", 1900, 17), ("03", 1910, 18), ("03", 1920, 49), ("03", 1930, 303),
    # ("03", 1940, 142), 
    ("03", 1950, 441), ("03", 1960, 1998), ("03", 1970, 12939),
    ("03", 1980, 16683), ("03", 1990, 20779), ("03", 2000, 27657),
    ("03", 2010, 25419), 
    # ("03", 2020, 5290),
    # ("60", 1760, 2), ("60", 1840, 1), 
    ("60", 1860, 3), 
    ("60", 1870, 120),
    ("60", 1880, 194), ("60", 1890, 65), ("60", 1900, 19), ("60", 1910, 12),
    ("60", 1920, 17), ("60", 1930, 128), 
    # ("60", 1940, 68), 
    ("60", 1950, 297),
    ("60", 1960, 2053), ("60", 1970, 22103), ("60", 1980, 34287),
    ("60", 1990, 37365), ("60", 2000, 45390),
    ("60", 2010, 49527), 
    # ("60", 2020, 13743)
]

df = pd.DataFrame(data, columns=["prefix", "decade", "count"])

# Plot
plt.figure(figsize=(10,6))

for prefix, label in [("03", "Logic (03*)"), ("60", "Probability (60*)")]:
    subset = df[df["prefix"] == prefix]
    plt.plot(subset["decade"], subset["count"], marker="o", label=label)

# Log scale for y-axis
plt.yscale("log")

# Annotate turning points
annotations = [
    (1930, 303, "Gödel 1931 (On formally undecidable propositions..)"), ## <https://zbmath.org/3001277>	"On formally undecidable propositions of \\textit{Principia Mathematica} and related systems. I"	"1931"^^<http://www.w3.org/2001/XMLSchema#gYear>	53
    (1970, 12939, "Zadeh 1965 (Fuzzy sets)"), ## <https://zbmath.org/3226241>	"Fuzzy sets"	"1965"^^<http://www.w3.org/2001/XMLSchema#gYear>	4794
    (1870, 120, "Probability rise"),
    # (1880, 98, "Logic rise"),
    (1930, 128, "Kolmogoroff 1933 (Grundbegriffe der \nWahrscheinlichkeitsrechnung)"), ## <https://zbmath.org/3010031>	"Grundbegriffe der Wahrscheinlichkeitsrechnung"	"1933"^^<http://www.w3.org/2001/XMLSchema#gYear>	44
    (1970, 22103, "Computing/AI boom")
]

for x, y, text in annotations:
    plt.annotate(text, xy=(x,y), xytext=(x+5, y*1.5),
                 arrowprops=dict(arrowstyle="->", lw=1))

# plt.title("Revival Highlight Plot: Logic vs Probability (MSC Prefix 03 & 60)")
plt.xlabel("Decade")
plt.ylabel("Publication count (log scale)")
plt.legend()
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.savefig("plot_revival.pdf")   # Save as PDF
plt.savefig("plot_revival.svg")   # Save as SVG
plt.show()
