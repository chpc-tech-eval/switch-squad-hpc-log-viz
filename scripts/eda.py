from pathlib import Path
from zipfile import ZipFile
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_FILE = "logs/2017-01-22.log"

records = []
bad_lines = []
blank_lines = 0

with ZipFile(ROOT / "logs.zip") as archive:
    lines = archive.read(SAMPLE_FILE).decode("utf-8-sig").splitlines()

for number, line in enumerate(lines, start=1):
    if not line.strip():
        blank_lines += 1
        continue

    parts = [part.strip() for part in line.split(",")]

    try:
        if len(parts) < 2:
            raise ValueError("No metrics found")

        record = {"timestamp": parts[0]}

        for part in parts[1:]:
            key, value = part.split("=", 1)
            key = key.strip()

            if not key or key in record:
                raise ValueError("Empty or repeated field name")

            record[key] = value.strip()

        records.append(record)

    except ValueError:
        bad_lines.append(number)

if not records:
    raise ValueError(
        "No records could be loaded. Share this error before continuing."
    )

frame = pd.DataFrame(records)

frame["timestamp"] = pd.to_datetime(
    frame["timestamp"],
    format="%Y-%m-%d %H:%M",
    errors="coerce",
)

for column in frame.columns:
    if column != "timestamp":
        values = (
            frame[column]
            .astype("string")
            .str.strip()
            .str.removesuffix("%")
        )
        frame[column] = pd.to_numeric(values, errors="coerce")

metrics = frame.drop(columns="timestamp")
valid_times = frame["timestamp"].dropna()

print("Pandas version:", pd.__version__)
print("Sample file:", SAMPLE_FILE)
print("Blank lines:", blank_lines)
print("Rows loaded:", len(frame))
print("Malformed line numbers:", bad_lines)
print("Fields found:", ", ".join(frame.columns))
print(
    "Unparseable timestamps:",
    int(frame["timestamp"].isna().sum()),
)
print("Sample starts:", valid_times.min())
print("Sample ends:", valid_times.max())
print(
    "Repeated timestamps (extra rows):",
    int(valid_times.duplicated().sum()),
)

print("\nNUMERIC SUMMARY")
print(
    metrics.describe()
    .loc[["count", "min", "max", "mean"]]
    .T.to_string()
)

print("\nMISSING OR INVALID NUMERIC VALUES")
print(metrics.isna().sum().to_string())

print("\nMOST COMMON GAPS BETWEEN DISTINCT TIMESTAMPS")
print(
    valid_times.drop_duplicates()
    .sort_values()
    .diff()
    .value_counts()
    .head(5)
    .to_string()
)
