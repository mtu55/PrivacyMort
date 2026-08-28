import argparse
import pandas as pd
import subprocess
from io import BytesIO

# init parser
parser = argparse.ArgumentParser()
parser.add_argument("file1")
parser.add_argument("file2")
args = parser.parse_args()

# First Excel
current_df = pd.read_excel(args.file1)

# Second Excel
second_df = pd.read_excel(args.file2)

# Compare

if current_df.equals(second_df):
    print("Identical")
else:
    print("Different")
    print(current_df.compare(second_df))
