# import pandas as pd
# import os

# INPUT = "/home/oloko/Documents/huawei_work/draft/sms_work/sms_sbin_Togba.csv"
# OUT_SUFFIX = "_with_duration.csv"

# df = pd.read_csv(INPUT)

# # find columns that look like time columns (handles "Time", "Time.1", etc.)
# time_cols = [c for c in df.columns if "time" in c.lower()]

# if len(time_cols) < 2:
#     raise ValueError(f"Need at least two time-like columns, found: {df.columns.tolist()}")

# # keep original order as in the dataframe
# t0_col, t1_col = time_cols[0], time_cols[1]

# def clean_and_parse(series):
#     # remove surrounding quotes and control chars like tabs/spaces, then parse
#     s = series.astype(str).str.strip().str.replace(r'["\t\r\n]', '', regex=True)
#     return pd.to_datetime(s, errors="coerce")

# df["_t0_parsed"] = clean_and_parse(df[t0_col])
# df["_t1_parsed"] = clean_and_parse(df[t1_col])

# # duration as timedelta and in milliseconds
# df["Duration"] = df["_t1_parsed"] - df["_t0_parsed"]
# df["Duration_s"] = df["Duration"].dt.total_seconds() 

# df["Duration"] = df["_t1_parsed"] - df["_t0_parsed"]
# # seconds only (float). If you want whole seconds (nullable int) use the commented line.


# #######optional: drop helper cols or keep for debugging
# df = df.drop(columns=["_t0_parsed", "_t1_parsed" , "Duration"])

# # write result next to input file
# out_path = os.path.splitext(INPUT)[0] + OUT_SUFFIX
# df.to_csv(out_path, index=False)

# # show a quick summary
# print(f"Used time cols: {t0_col}, {t1_col}")
# print(f"Parsed durations (non-null): {df['Duration_ms'].notna().sum()} / {len(df)}")
# print(df[["Duration", "Duration_ms"]].head())










import os
import glob
import pandas as pd

INPUT_DIR = "/home/oloko/Documents/huawei_work/draft/sms_work/raw"
OUT_DIR = os.path.join(INPUT_DIR, "duration")
OUT_SUFFIX = "_with_duration.csv"

os.makedirs(OUT_DIR, exist_ok=True)

def clean_and_parse(series):
    s = series.astype(str).str.strip().str.replace(r'["\t\r\n]', '', regex=True)
    return pd.to_datetime(s, errors="coerce")

for path in glob.glob(os.path.join(INPUT_DIR, "*.csv")):
    # skip files already in the output directory
    if os.path.commonpath([os.path.abspath(path), os.path.abspath(OUT_DIR)]) == os.path.abspath(OUT_DIR):
        continue

    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"Skipping {os.path.basename(path)}: read error: {e}")
        raise Exception(f"Read error: {e}")
        continue

    time_cols = [c for c in df.columns if "time" in c.lower()]
    if len(time_cols) < 2:
        print(f"Skipping {os.path.basename(path)}: need >=2 time-like columns, found {len(time_cols)}")
        raise Exception(f"Need at least two time-like columns, found: {df.columns.tolist()}")
        continue

    t0_col, t1_col = time_cols[0], time_cols[1]

    df["_t0_parsed"] = clean_and_parse(df[t0_col])
    df["_t1_parsed"] = clean_and_parse(df[t1_col])

    # seconds only (float); NaN for rows that failed parsing
    df["Duration_s"] = (df["_t1_parsed"] - df["_t0_parsed"]).dt.total_seconds()

    # drop helper parsed cols, keep original time columns and other data
    df = df.drop(columns=["_t0_parsed", "_t1_parsed"])

    out_name = os.path.splitext(os.path.basename(path))[0] + OUT_SUFFIX
    out_path = os.path.join(OUT_DIR, out_name)
    try:
        df.to_csv(out_path, index=False)
    except Exception as e:
        print(f"Failed to write {out_path}: {e}")
        continue

    print(f"Processed {os.path.basename(path)} -> {out_path} | used: {t0_col}, {t1_col}")