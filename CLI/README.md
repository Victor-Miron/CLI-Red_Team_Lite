## Local Inventory Collector and CLI(Command Line Interface) Analyzer

This project is a Python3 based system inventory and analysis tool that collects information from a local Linux machine and provides a CLI to analyze and manage data collected.

project/
│
├── collector.py              # Collects system information
├── inventory_cli.py          # CLI analyzer
├── README.md
│
├── json_files/              # Inventory JSON files
    ├── inventory_compare.json
│   ├── inventory1.json
│   ├── inventory2.json
    ├── inventory3.json
│   └── inventory4.json
│
├── report/                   # Project documentation
│   ├── report.md
│   └── report.pdf

### Part 1 Local Inventory Collector

Step 1 – Collect Basic System Info

    - Hostname
    - Operating system name and version

Step 2 – Collect Open Ports
    - Identify likely listening/open local ports using local system commands

Step 3 – Collect Installed Software Count

    - Gather a basic list of installed applications or packages count

Step 4 – Build JSON Output

    - Store all collected data in a Python dictionary.

Step 5 – Save to File

Write the inventory to a folder such as:

    - json_files


### Part 2 – Inventory CLI Analyzer

The CLI tool loads one or more JSON inventory files from a folder and provides useful commands for a SOC analyst.

## Supported Commands:

   - list-assets
   - filter-os
   - risky-hosts
   - compare-assets

## 1.Load all JSON files from a folder 

     - python3 inventory_cli.py list-assets --folder json_files

     Hostname             OS              Open Ports      Software Count 
    ------------------------------------------------------------------
    cyberlab             Linux           10             2141           
    kali                 Linux           12             2885           
    macbook-pro-01       macOS           2              220            
    fake_user            Windows         16             2885  

##  2.Command: filter-os
    Filter assets by operating system.

    python3 inventory_cli.py filter-os Linux --folder json_files

    Hostname             OS              Open Ports     Software Count 
    ------------------------------------------------------------------
    cyberlab             Linux           10             2141           
    kali                 Linux           12             2885  

## 3.Command: risky-hosts
    Displays hosts with Medium, High or Critical risk levels.
    - python3 inventory_cli.py risky-hosts --folder json_files

    Hostname             Score           Risk Level      Notes               
    ------------------------------------------------------------------
    kali                 4               Medium          Port 445 open
    macbook-pro-01       3               Medium          Port 22 open
    fake_user            10              Critical        Port 3389 open, Port 22 open, Port 445 open

## 3.Command: compare-assets
Compare two inventory files to detect differences.

python3 inventory_cli.py compare-assets json_files/inventory1.json json_files/inventory_compare.json

Comparing inventory.json and inventory_compare.json
------------------------------------------------------------------
Hostnames: cyberlab | cyberlab
Operating System: Linux (no change)
Software Count: 2402 -> 2402 (+0)

Ports added:
None

Ports removed:
None

Software added:
None

Software removed:
None

## Risk Factors

    +2 points -> more than 10 open ports
    +3 points -> port 3389 is open
    +3 points -> port 22 is open
    +2 points -> port 445 is open
    +1 point -> software count is unusually high
    +2 points -> key data is missing

## Priority Labels

        0–2 = Low
        3–5 = Medium
        6–8 = High
        9+ = Critical

## Notes
- This project is intended for educational purposes
- All data collection is performed locally
- The tool uses simple parsing techniques and does not rely on external APIs