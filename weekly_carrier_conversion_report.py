#!/usr/bin/env python3
"""
Weekly Carrier Conversion Report

Usage:
    python weekly_carrier_conversion_report.py assignments.csv loads.csv
    python weekly_carrier_conversion_report.py assignments.xlsx loads.xlsx

Required assignment columns:
    Rep
    Carrier
    DOT

Required booked load columns:
    Carrier
    DOT
    Load

Output:
    Weekly_Carrier_Conversion_Report.xlsx
"""

import argparse
from pathlib import Path
import pandas as pd


ASSIGNMENT_REQUIRED_COLUMNS = ["Rep", "Carrier Name", "DOT"]
LOAD_REQUIRED_COLUMNS = ["Carrier Name", "Load ID"]


def read_input_file(file_path: str) -> pd.DataFrame:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path, dtype=str)
    elif suffix in [".xlsx", ".xls"]:
        return pd.read_excel(path, dtype=str)
    else:
        raise ValueError("Unsupported file type. Please use CSV or Excel.")


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    def apply_column_aliases(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    aliases = {
        "Carrier": "Carrier Name",
        "Load": "Load ID",
    }

    df = df.rename(columns={col: aliases[col] for col in df.columns if col in aliases})

    return df


def validate_columns(df: pd.DataFrame, required_columns: list[str], file_label: str) -> None:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"{file_label} is missing required columns: {missing}. "
            f"Available columns: {list(df.columns)}"
        )


def clean_dot(value) -> str:
    if pd.isna(value):
        return ""

    value = str(value).strip()

    # Handle DOT values that come in as 123456.0 from Excel
    if value.endswith(".0"):
        value = value[:-2]

    # Keep only digits
    value = "".join(ch for ch in value if ch.isdigit())

    return value


def clean_carrier_name(value) -> str:
    if pd.isna(value):
        return ""

    return " ".join(str(value).strip().upper().split())


def prepare_assignments(assignments: pd.DataFrame) -> pd.DataFrame:
    assignments = normalize_column_names(assignments)
    validate_columns(assignments, ASSIGNMENT_REQUIRED_COLUMNS, "Assignment file")

    output = assignments[ASSIGNMENT_REQUIRED_COLUMNS].copy()

    output["Rep"] = output["Rep"].fillna("").astype(str).str.strip()
    output["Carrier Name"] = output["Carrier Name"].apply(lambda x: "" if pd.isna(x) else str(x).strip())
    output["DOT"] = output["DOT"].apply(clean_dot)
    output["Carrier Name Clean"] = output["Carrier Name"].apply(clean_carrier_name)

    # Remove completely blank rows
    output = output[
        (output["Rep"] != "") |
        (output["Carrier Name"] != "") |
        (output["DOT"] != "")
    ].copy()

    # Keep one row per Rep + DOT + Carrier combination
    output = output.drop_duplicates(subset=["Rep", "DOT", "Carrier Name Clean"])

    return output


def prepare_loads(loads: pd.DataFrame) -> pd.DataFrame:
    loads = normalize_column_names(loads)
    loads = apply_column_aliases(loads)
    validate_columns(loads, LOAD_REQUIRED_COLUMNS, "Load file")

    output_columns = ["Carrier Name", "Load ID"]

    if "DOT" in loads.columns:
        output_columns.append("DOT")

    output = loads[output_columns].copy()

    if "DOT" not in output.columns:
        output["DOT"] = ""

    output["Carrier Name"] = output["Carrier Name"].apply(lambda x: "" if pd.isna(x) else str(x).strip())
    output["DOT"] = output["DOT"].apply(clean_dot)
    output["Load ID"] = output["Load ID"].fillna("").astype(str).str.strip()
    output["Carrier Name Clean"] = output["Carrier Name"].apply(clean_carrier_name)

    # Remove rows without a load id
    output = output[output["Load ID"] != ""].copy()

    return output


def build_report(assignments: pd.DataFrame, loads: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    assignments_clean = prepare_assignments(assignments)
    loads_clean = prepare_loads(loads)

        # Prefer DOT matching when available, otherwise match by cleaned carrier name
    if loads_clean["DOT"].str.strip().ne("").any():
        loads_grouped = (
            loads_clean[loads_clean["DOT"] != ""]
            .groupby("DOT", as_index=False)
            .agg(
                Loads_Booked=("Load ID", "nunique"),
                Load_IDs=("Load ID", lambda x: ", ".join(sorted(set(x))))
            )
        )

        carrier_detail = assignments_clean.merge(
            loads_grouped,
            on="DOT",
            how="left"
        )
    else:
        loads_grouped = (
            loads_clean
            .groupby("Carrier Name Clean", as_index=False)
            .agg(
                Loads_Booked=("Load ID", "nunique"),
                Load_IDs=("Load ID", lambda x: ", ".join(sorted(set(x))))
            )
        )

        carrier_detail = assignments_clean.merge(
            loads_grouped,
            on="Carrier Name Clean",
            how="left"
        )

    carrier_detail["Loads_Booked"] = carrier_detail["Loads_Booked"].fillna(0).astype(int)
    carrier_detail["Load_IDs"] = carrier_detail["Load_IDs"].fillna("")
    carrier_detail["Converted"] = carrier_detail["Loads_Booked"].apply(lambda x: "Yes" if x >= 1 else "No")

    carrier_detail = carrier_detail[
        ["Rep", "Carrier Name", "DOT", "Loads_Booked", "Converted", "Load_IDs"]
    ].sort_values(["Rep", "Converted", "Loads_Booked", "Carrier Name"], ascending=[True, True, False, True])

    rep_scorecard = (
        carrier_detail
        .groupby("Rep", as_index=False)
        .agg(
            Assigned_Carriers=("DOT", "count"),
            Converted_Carriers=("Converted", lambda x: (x == "Yes").sum()),
            Total_Loads_Booked=("Loads_Booked", "sum")
        )
    )

    rep_scorecard["Conversion_Rate"] = (
        rep_scorecard["Converted_Carriers"] / rep_scorecard["Assigned_Carriers"]
    )

    rep_scorecard["Loads_Per_Assigned_Carrier"] = (
        rep_scorecard["Total_Loads_Booked"] / rep_scorecard["Assigned_Carriers"]
    )

    rep_scorecard["Loads_Per_Converted_Carrier"] = rep_scorecard.apply(
        lambda row: row["Total_Loads_Booked"] / row["Converted_Carriers"]
        if row["Converted_Carriers"] > 0 else 0,
        axis=1
    )

    rep_scorecard = rep_scorecard[
        [
            "Rep",
            "Assigned_Carriers",
            "Converted_Carriers",
            "Conversion_Rate",
            "Total_Loads_Booked",
            "Loads_Per_Assigned_Carrier",
            "Loads_Per_Converted_Carrier",
        ]
    ].sort_values(
        ["Conversion_Rate", "Total_Loads_Booked"],
        ascending=[False, False]
    )

    return rep_scorecard, carrier_detail


def export_report(rep_scorecard: pd.DataFrame, carrier_detail: pd.DataFrame, output_file: str) -> None:
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        rep_scorecard.to_excel(writer, sheet_name="Rep Scorecard", index=False)
        carrier_detail.to_excel(writer, sheet_name="Carrier Detail", index=False)

        workbook = writer.book

        scorecard_ws = writer.sheets["Rep Scorecard"]
        detail_ws = writer.sheets["Carrier Detail"]

        # Format percent columns
        for cell in scorecard_ws["D"][1:]:
            cell.number_format = "0.00%"

        # Format decimal metric columns
        for col_letter in ["F", "G"]:
            for cell in scorecard_ws[col_letter][1:]:
                cell.number_format = "0.00"

        # Auto-width columns
        for worksheet in [scorecard_ws, detail_ws]:
            for column_cells in worksheet.columns:
                max_length = 0
                column_letter = column_cells[0].column_letter

                for cell in column_cells:
                    value = "" if cell.value is None else str(cell.value)
                    max_length = max(max_length, len(value))

                worksheet.column_dimensions[column_letter].width = min(max_length + 2, 60)


def main():
    parser = argparse.ArgumentParser(description="Create a weekly carrier conversion report.")
    parser.add_argument("assignments_file", help="Weekly assignment file, CSV or Excel")
    parser.add_argument("loads_file", help="Weekly booked loads file, CSV or Excel")
    parser.add_argument(
        "-o",
        "--output",
        default="Weekly_Carrier_Conversion_Report.xlsx",
        help="Output Excel file name"
    )

    args = parser.parse_args()

    assignments = read_input_file(args.assignments_file)
    loads = read_input_file(args.loads_file)

    rep_scorecard, carrier_detail = build_report(assignments, loads)

    export_report(rep_scorecard, carrier_detail, args.output)

    print(f"Report created: {args.output}")
    print()
    print("Rep Scorecard Preview:")
    print(rep_scorecard.to_string(index=False))


if __name__ == "__main__":
    main()
