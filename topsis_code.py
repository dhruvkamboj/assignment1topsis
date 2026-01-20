import sys
import os
import pandas as pd
import numpy as np

def read_input_file(file_path):
    if not os.path.exists(file_path):
        print("Error: Input file not found.")
        sys.exit(1)

    try:
        if file_path.lower().endswith(".csv"):
            return pd.read_csv(file_path)
        elif file_path.lower().endswith((".xlsx", ".xls")):
            return pd.read_excel(file_path)
        else:
            print("Error: Unsupported file format. Use CSV or Excel.")
            sys.exit(1)
    except Exception as e:
        print("Error reading file:", e)
        sys.exit(1)

def topsis(input_file, weights, impacts, output_file):

    # ---------- Read Input ----------
    df = read_input_file(input_file)

    # ---------- Column Check ----------
    if df.shape[1] < 3:
        print("Error: Input file must contain at least 3 columns.")
        sys.exit(1)

    # First column is identifier (NOT used in calculation)
    decision_matrix = df.iloc[:, 1:]

    # ---------- Numeric Check ----------
    if not decision_matrix.apply(pd.to_numeric, errors='coerce').notnull().all().all():
        print("Error: From 2nd to last columns must contain numeric values only.")
        sys.exit(1)

    # ---------- Parse Weights & Impacts ----------
    weights = weights.split(",")
    impacts = impacts.split(",")

    if len(weights) != decision_matrix.shape[1]:
        print("Error: Number of weights must match number of criteria.")
        sys.exit(1)

    if len(impacts) != decision_matrix.shape[1]:
        print("Error: Number of impacts must match number of criteria.")
        sys.exit(1)

    for i in impacts:
        if i not in ['+', '-']:
            print("Error: Impacts must be either '+' or '-'.")
            sys.exit(1)

    weights = np.array(weights, dtype=float)

    # ---------- Step 1: Normalize ----------
    norm_matrix = decision_matrix / np.sqrt((decision_matrix ** 2).sum())

    # ---------- Step 2: Weighted Normalized Matrix ----------
    weighted_matrix = norm_matrix * weights

    # ---------- Step 3: Ideal Best & Worst ----------
    ideal_best = []
    ideal_worst = []

    for i in range(len(impacts)):
        if impacts[i] == '+':
            ideal_best.append(weighted_matrix.iloc[:, i].max())
            ideal_worst.append(weighted_matrix.iloc[:, i].min())
        else:
            ideal_best.append(weighted_matrix.iloc[:, i].min())
            ideal_worst.append(weighted_matrix.iloc[:, i].max())

    ideal_best = np.array(ideal_best)
    ideal_worst = np.array(ideal_worst)

    # ---------- Step 4: Distance Calculation ----------
    dist_best = np.sqrt(((weighted_matrix - ideal_best) ** 2).sum(axis=1))
    dist_worst = np.sqrt(((weighted_matrix - ideal_worst) ** 2).sum(axis=1))

    # ---------- Step 5: TOPSIS Score ----------
    topsis_score = dist_worst / (dist_best + dist_worst)

    # ---------- Step 6: Rank ----------
    ranks = topsis_score.rank(ascending=False, method='dense')

    # ---------- Output ----------
    result = df.copy()
    result["Topsis Score"] = topsis_score
    result["Rank"] = ranks.astype(int)

    # Save output
    try:
        result.to_csv(output_file, index=False)
    except Exception as e:
        print("Error writing output file:", e)
        sys.exit(1)

    print("TOPSIS analysis completed successfully.")
    print("Output saved to:", output_file)


# ================= MAIN =================
if __name__ == "__main__":

    if len(sys.argv) != 5:
        print("Usage:")
        print("python topsis.py <InputDataFile> <Weights> <Impacts> <OutputResultFileName>")
        sys.exit(1)

    input_file = sys.argv[1]
    weights = sys.argv[2]
    impacts = sys.argv[3]
    output_file = sys.argv[4]

    topsis(input_file, weights, impacts, output_file)
