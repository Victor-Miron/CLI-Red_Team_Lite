import socket
import platform
import os
import json


def get_hostname():
    return socket.gethostname()


def get_os_info():
    return {
        "Operating System": platform.system(),
        "OS Version": platform.version(),
        "Kernel Version": platform.release(),
        "Architecture": platform.architecture()[0],
        }
            


def get_installed_software():
    out = os.popen("dpkg -l").read()
    softwre = []

    for line in out.splitlines():
        if line.startswith("ii"):
            words = line.split()
            softwre.append(words[1])

    return softwre, len(softwre)


def get_open_ports():
    result = os.popen("ss -tuln").read()
    ports = []

    for line in result.splitlines():
        words = line.split()
        if len(words) < 5:
            continue
        
        if words[0] in ("tcp", "udp"):
            local_address = words[4]
            port = local_address.rsplit(":", 1)[-1]

            if port.isdigit():
                ports.append(port)

    return sorted(set(ports))


def build_inventory():
    software, software_count = get_installed_software()
    return {
        "hostname": get_hostname(),
        "system": get_os_info(),
        "software": software,
        "software_count": software_count,
        "ports": get_open_ports(),
        
    }


def save_inventory_to_json():
    inventory = build_inventory()
    with open("json_files/inventory1.json", "w") as file:
        json.dump(inventory, file, indent=4)
    print("Inventory saved to json_files/inventory1.json")


def main():
    save_inventory_to_json()


if __name__ == "__main__":
    main()
    


