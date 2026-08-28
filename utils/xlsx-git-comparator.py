import argparse
import pandas as pd
import subprocess
from io import BytesIO

# init parser
parser = argparse.ArgumentParser()
parser.add_argument("file1")
args = parser.parse_args()

# current Excel
current_df = pd.read_excel(args.file1)

# Last committed Excel
result = subprocess.run(
    ["git", "show", f"HEAD:{args.file1}"],
    capture_output=True,
    check=True,
)
committed_file = BytesIO(result.stdout)
committed_df = pd.read_excel(committed_file)

# Compare

if current_df.equals(committed_df):
    print("Identical")
else:
    print("Different")
    print(current_df.compare(committed_df))
