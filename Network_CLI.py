import socket
import time


class NetworkEngine:
    """
    Backend: Handles all network sockets, port scanning,
    and connection logic. It does not touch the file system.
    """

    def __init__(self):
        # You can store scan history or target profiles here later
        self.scan_history = []

    def nmap(self, *args):
        """
        nmap function: Scans a target IP for open ports.
        Format: nmap <ip>
        """
        if len(args) < 2:
            print("nmap: missing target IP operand")
            return

        target_ip = args[1]
        common_ports = [21, 22, 80, 139, 443, 8080]

        print(f"\nStarting Mini-NMAP scan against {target_ip}...")
        print("PORT\t\tSTATE")
        print("-" * 30)

        for port in common_ports:
            # Create IPv4 TCP socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)  # Prevent the GUI from freezing too long

            # connect_ex returns 0 on success, or an error code
            result = s.connect_ex((target_ip, port))
            s.close()

            if result == 0:
                print(f"{port}/tcp\t\topen")
            # Closed ports are omitted for cleaner output, just like real NMAP
        print("Scan finished.\n")

    def ping(self, *args):
        """ ping function
                Checks if a target host is responsive by opening a quick TCP connection.

                Format:
                >ping <ip_or_domain>   : Pings the target host 4 times and prints latency.
            """
        if len(args) < 2:
            print("ping: missing target operand")
            return

        target = args[1]
        port = 80  # Use standard HTTP port for a quick responsiveness check
        print(f"\nPING {target} on TCP port {port}:")

        success_count = 0
        total_time = 0

        # Run 4 ping cycles (standard terminal behaviour)
        for i in range(4):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.5)  # Time out quickly if host is offline

            # Start the high-precision timer
            start_time = time.perf_counter()

            try:
                # Attempt connection
                result = s.connect_ex((target, port))
                # Stop the timer immediately after connection attempt returns
                end_time = time.perf_counter()

                # Calculate latency in milliseconds
                latency = (end_time - start_time) * 1000

                if result == 0 or result == 10061:
                    # Note: Error 10061 means "Connection Refused" which actually
                    # proves the host is alive and actively blocking the port!
                    print(f"Reply from {target}: time={latency:.2f}ms")
                    success_count += 1
                    total_time += latency
                else:
                    print(f"Request timed out. (Error code: {result})")

            except socket.gaierror:
                print(f"ping: unknown host {target}")
                s.close()
                return
            finally:
                s.close()

            # Brief pause between packet cycles (100ms) to prevent flood flags
            time.sleep(0.1)

        # Print statistics summary
        if success_count > 0:
            avg_time = total_time / success_count
            print(f"\n--- {target} ping statistics ---")
            print(f"Packets: Sent = 4, Received = {success_count}, Lost = {4 - success_count}")
            print(f"Approximate round trip times: Average = {avg_time:.2f}ms\n")
        else:
            print(f"\n--- {target} ping statistics ---")
            print("Packets: Sent = 4, Received = 0, Lost = 4 (100% loss)\n")
