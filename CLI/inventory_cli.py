import argparse
import json
import os


def load_inventory_file(filename):
    with open(filename, "r") as f:
        return json.load(f)


def load_multiple_inventories(folder_path):
    inventories = []
    files = os.listdir(folder_path)
    
    for file in files:
        if file.endswith(".json"):
            file_path = os.path.join(folder_path, file)

            with open(file_path, "r") as f:
                inventories.append(json.load(f))
    return inventories


def list_assets(inventories):
    if isinstance(inventories, dict):
        inventories = [inventories]

    print(f"{'Hostname':<20} {'OS':<15} {'Open Ports':<15} {'Software Count':<15}")
    print("-" * 66)

    for asset in inventories:
        hostname = asset.get('hostname')
        os_name = asset.get('system', {}).get('Operating System', "N/A")
        open_ports = asset.get("ports", [])
        software_count = asset.get("software_count", 0)
        print(f"{hostname:<20} {os_name:<15} {len(open_ports):<15} {software_count:<15}")
        


def filter_by_os(inventories, os_name):
    assets_filtered = []
    for asset in inventories:
        system_os = asset.get('system', {}).get('Operating System', "")
        if system_os.lower() == os_name.lower():
            assets_filtered.append(asset)
        
    return assets_filtered


def calculate_risk_score(asset):
    score = 0
    ports = asset.get("ports", [])
    software = asset.get("software", [])
    notes = []
    
    if "3389" in ports:
        score += 3
        notes.append("Port 3389 open")
    if "22" in ports:
        score += 3
        notes.append("Port 22 open")
    if len(ports) >= 10:
        score += 2
    if "445" in ports:
        score += 2
        notes.append("Port 445 open")
    if len(software) > 3000:
        score += 1
        notes.append("High software count")

    if not asset.get("hostname") or not asset.get("system"):
        score += 2
        notes.append("Missing critical system info")

    return score, ", ".join(notes)


def classify_risk(score):
    
    if 0 <= score <= 2:
        return "Low"
    elif 3 <= score <= 5:
        return "Medium"
    elif 6 <= score < 9:
        return "High"
    else:
        return "Critical"


def show_risky_hosts(inventories):
    found = False

    print(f"{'Hostname':<20} {'Score':<15} {'Risk Level':<15} {'Notes':<20}")
    print("-" * 66)

    for asset in inventories:
        score, notes = calculate_risk_score(asset)
        priority = classify_risk(score)

        if priority in ("Medium", "High", "Critical"):
            hostname = asset.get("hostname", "N/A")
            print(f"{hostname:<20} {score:<15} {priority:<15} {notes}")
            found = True

    if not found:
        print("No medium, high or critical risk hosts.")


def compare_software(asset1, asset2):
    software1 = set(asset1.get("software", []))
    software2 = set(asset2.get("software", []))

    added = sorted(software2 - software1)
    removed = sorted(software1 - software2)

    return added, removed


def compare_assets(file1, file2):
    asset1 = load_inventory_file(file1)
    asset2 = load_inventory_file(file2)

    print(f"Comparing {os.path.basename(file1)} and {os.path.basename(file2)}")
    print("-" * 66)

    hostname1 = asset1.get("hostname", "N/A")
    hostname2 = asset2.get("hostname", "N/A")
    print(f"Hostnames: {hostname1} | {hostname2}")

    os1 = asset1.get("system", {}).get("Operating System", "N/A")
    os2 = asset2.get("system", {}).get("Operating System", "N/A")
    if os1 == os2:
        print(f"Operating System: {os1} (no change)")
    else:
        print(f"Operating System: {os1} -> {os2}")

    software_count1 = asset1.get("software_count", 0)
    software_count2 = asset2.get("software_count", 0)
    diff = software_count2 - software_count1

    print(f"Software Count: {software_count1} -> {software_count2} ({diff:+})")

    ports1 = set(asset1.get("ports", []))
    ports2 = set(asset2.get("ports", []))

    added_ports = sorted(ports2 - ports1, key=int)
    removed_ports = sorted(ports1 - ports2, key=int)

    print("\nPorts added:")
    if added_ports:
        for port in added_ports:
            print(f"- {port}")
    else:
        print("None")

    print("\nPorts removed:")
    if removed_ports:
        for port in removed_ports:
            print(f"- {port}")
    else:
        print("None")

    added_software, removed_software = compare_software(asset1, asset2)

    print("\nSoftware added:")
    if added_software:
        for soft in added_software[:20]:
            print(f"- {soft}")
        if len(added_software) > 20:
            print(f"{len(added_software) - 20} more entries")
    else:
        print("None")

    print("\nSoftware removed:")
    if removed_software:
        for soft in removed_software[:20]:
            print(f"- {soft}")
        if len(removed_software) > 20:
            print(f"{len(removed_software) - 20} entries removed")
    else:
        print("None")
        

def cmd_list(args):
    inventories = load_multiple_inventories(args.folder)
    list_assets(inventories)


def cmd_filter(args):
    inventories = load_multiple_inventories(args.folder)
    inventories = filter_by_os(inventories, args.os_name)
    list_assets(inventories)


def cmd_risk(args):
    inventories = load_multiple_inventories(args.folder)
    show_risky_hosts(inventories)


def cmd_compare(args):
    compare_assets(args.file1, args.file2)


def build_parser():
    parser = argparse.ArgumentParser(description="Inventory CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    parser_list = sub.add_parser("list-assets", help="List assets")
    parser_list.add_argument("--folder", default="json_files")
    parser_list.set_defaults(func=cmd_list)

    parser_os = sub.add_parser("filter-os", help="Filter assets by operating systems")
    parser_os.add_argument("os_name")
    parser_os.add_argument("--folder", default="json_files")
    parser_os.set_defaults(func=cmd_filter)

    parser_risk = sub.add_parser("risky-hosts", help="Show risky hosts")
    parser_risk.add_argument("--folder", default="json_files")
    parser_risk.set_defaults(func=cmd_risk)
    
    parser_compare = sub.add_parser("compare-assets", help="Compare two inventory files")
    parser_compare.add_argument("file1")
    parser_compare.add_argument("file2")
    parser_compare.set_defaults(func=cmd_compare)
    
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
   

if __name__ == "__main__":
    main()


