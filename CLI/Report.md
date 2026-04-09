 ## 1.Overview
The CLI tool is designed to gather information about the local systems, save them in JSON files and then analyze the vulnerability risks that are found using some risk levels.

## 2.Inventory Collection
The data was collected using different libraries in python and gathered the following:
- Operating Systems - library used: platform
	- OS Version
	- Kernel Version
	- Architecture
- Open Ports - library used: "os" - "ss -tuln"
	- The target was to find vulnerable open ports that have more chances of being exploited like: 
		- 3389 - remote desktop protocol 
			- used for remote control of Windows machines
			- give full desktop access
			- Risk:
				- used in ransomware attacks
				- very high risk if open
		- 22 - secure shell 
			- Risk:
				- brute-force attacks(password guessing)
				- if exposed to the internet -frequently targeted
		- 445 - SMB (Server Message Block)
			- Used for file sharing in Windows networks
			- network file sharing
			- shared drives
			- Risk:
				- Vulnerable exploits(WannaCry ransomware)
				- very dangerous if exposed externally

The script was tested on a Linux system and it is limited to collecting data just from other Linux systems. Although its limitations, the script can recognize and analyze other operating systems as long as the data collected is imported from other sources. There are other systems like macOS and Windows json files used for testing in the JSON_FILES folder. 

## 3.CLI Analysis
The program was designed to gather local information from a system and store them in a JSON folder. All the information then will be used to analyze the data. The only limitation right now is that you cannot analyze individual files from the JSON folder, but that can be improved.
There are four major commands used for the program:
- list-assets
	- python3 inventory_cli.py list-assets --folder json_files
- filter-os
	- python3 inventory_cli.py filter-os Linux --folder json_files
- risky-hosts
	- python3 inventory_cli.py risky-hosts --folder json_files

- compare-assets
    - python3 inventory_cli.py compare-assets json_files/inventory1.json json_files/inventory_compare.json
    - This command compares two inventory files and shows differences in:
        - software count
        - open ports (added/removed)
        - installed software (added/removed)
        - operating system changes


## Risk Logic
The risk was set up using a point system to be easier to determine the risk level later. There were 3 points for major risks, 2 points for medium risks, and 1 point for lower risks.
The system will sum up those points and then will put in the following categories:
- 0–2 = Low
- 3–5 = Medium
- 6–8 = High
- 9+ = Critical

The system will also display some notes for each system, specifying what the vulnerabilities were found and make the task easier to patch.

Having a point system has limitations because there is no certain way to know which vulnerability is higher, but having a starting point for the most common vulnerabilities, makes the system a little more secure.

## 5.Findings

- python3 inventory_cli.py risky-hosts --folder json_files

  

Hostname      Score     Risk Level       Notes
----------------------------------------------------------------
kali            4       Medium  Port     445 open
macbook-pro-01  3       Medium  Port     22 open
fake_user       10      Critical Port    3389 open, Port 22 open, Port 445 open
	
There were 4 assets analyzed and as it can be seen in the table above, just three of them show up, and that's because the program was set up to show just Medium, High and Critical systems and avoid bloating.
The systems analyzed were:
	- Linux Mint - which is not here because it has a lower risk
	- Kali - which is a Medium risk and as seen on notes, port 445 is open, which is a very known vulnerability for file sharing in Windows and got 2 points. Other points could be for the high length of the software installed or key data missing.
	- macbook-pro-01 - this system is a macOS system and it shows a medium risk, with the note of port 22 open, which is an ssh port.
	- fake_user - this is the system that will ring the bells in the church. As you can see, all the major risk ports are open and other risks involved that contribute to its score.

## 6.Recommendations

- Ports 3389(RDP), 22(SSH), 445(SMB) should be carefully secured because they provide remote access or file-sharing capabilities.
- Port 3389 should not be exposed to the internet and should be protected using VPNs, strong authentication and firewall restrictions.
- Port 22 should use key-based authentication, disable password logins and restrict access to trusted IP addresses
- SMB should never be exposed externally, should be limited to internal networks and must be kept updated and secured to prevent exploitation.

## 7.Reflection
The harder part of the project was to create the README and Report files. There are templates and other criteria but the challenge is to try to look professional but also understandable for tech and non-tech people. As for the python script, I became a fan of creating commands with argparse and I will use it in the future. It was a little tricky the load_multiple_inventories() function, but I had it figured out. What I would improve is the program to collect info from different type of systems and also choose single files for analysis.