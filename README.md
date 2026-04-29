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


**UPDATE**

Carrier Conversion Report Tool

A lightweight analytics tool that measures how newly onboarded carriers convert into booked loads and generates rep-level performance scorecards.

Overview

This tool was built to solve a common operational gap: lack of visibility into whether newly onboarded carriers actually produce load volume.

It automates the process of matching assigned carriers to booked loads and outputs clear performance metrics that can be used for coaching and decision-making.

Problem

Carrier reps were onboarding new carriers, but there was no structured way to measure:

Which carriers converted into booked loads
How much volume those carriers produced
Which reps were onboarding productive vs non-productive carriers

Solution

Built a Python-based reporting tool that:

Ingests weekly assignment and load data
Matches carriers using unique identifiers
Calculates conversion rates and load volume
Outputs rep-level scorecards and carrier-level detail

Packaged as a standalone executable so non-technical users can run it without installing Python.

Features

Automated carrier-to-load matching
Rep-level conversion metrics
Carrier-level performance detail for coaching
Case-insensitive column handling for real-world data compatibility
Auto-generated report naming by date
No dependencies required for end users

Quick Start

Place the following files in the same folder as the executable:

assignments.csv
Required columns:

Rep
Carrier Name
DOT

loads.csv
Required columns:

Carrier Name
DOT
Load ID
Run the tool:
Windows: double-click CarrierConversionReport.exe
Mac: run ./CarrierConversionReport
Open the generated file:
Weekly_Carrier_Conversion_Report_YYYY-MM-DD.xlsx

Output

Rep Scorecard

Assigned Carriers
Converted Carriers
Conversion Rate
Total Loads Booked

Carrier Detail

Load counts per carrier
Conversion status
Used for coaching and performance review

Usage

Run weekly (typically Thursday afternoon)
Review results prior to team meetings
Use carrier-level detail for rep coaching and performance discussions

Tech Stack

Python
Pandas
OpenPyXL
PyInstaller
GitHub Actions (for cross-platform builds)

Impact

Eliminated manual tracking of carrier conversion
Enabled consistent, data-driven coaching
Improved visibility into carrier quality and rep performance

Future Improvements

Follow-up tracking automation
Lane-level performance analysis
Carrier quality scoring
Web-based interface for broader accessibility
