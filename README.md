# weekly_carrier_conversion_report
Python tool for tracking carrier conversion performance by rep. Matches weekly onboarded carriers to booked loads using DOT, and outputs conversion rates, load volume, and carrier-level detail.

# Weekly Carrier Conversion Report

This script compares weekly assigned carriers against weekly booked loads.

## Required Input 1: Assignments File

Required columns:

- Rep
- Carrier Name
- DOT

## Required Input 2: Booked Loads File

Required columns:

- Carrier Name
- DOT
- Load ID

Extra columns are ignored.

## Run the Script

```bash
python weekly_carrier_conversion_report.py assignments.csv loads.csv
```

Or:

```bash
python weekly_carrier_conversion_report.py assignments.xlsx loads.xlsx
```

## Output

The script creates:

```text
Weekly_Carrier_Conversion_Report.xlsx
```

With two tabs:

1. Rep Scorecard
2. Carrier Detail

## Matching Logic

The first version uses DOT-only matching.

A carrier is considered converted if they have at least one unique Load ID in the booked loads file.
