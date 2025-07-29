import ipaddress
import subprocess

def ping_subnet(subnet):
    try:
        # Create an IPv4 network object
        network = ipaddress.ip_network(subnet, strict=False)
        
        print(f"Pinging all hosts in subnet: {subnet}")
        
        for ip in network.hosts():  # Iterate over all usable IPs in the subnet
            ip = str(ip)
            try:
                # Run the ping command
                result = subprocess.run(
                    ["ping", "-n", "1", ip],  # For Windows, replace with ["ping", "-n", "1", ip]
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                if result.returncode == 0:
                    print(f"{ip} is reachable")
                else:
                    print(f"{ip} is not reachable")
            except Exception as e:
                print(f"Error pinging {ip}: {e}")
    except ValueError as e:
        print(f"Invalid subnet: {e}")

# Example usage
subnet = "160.136.4.0/24"  # Replace with your desired subnet
ping_subnet(subnet)
