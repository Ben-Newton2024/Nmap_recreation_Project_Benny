import socket
import threading
import time


class NetworkEngine:

    def __init__(self):
        self.scan_history = []
        # Store the active background server socket here, so we can close it on exit
        self.server_socket = None
        self.listening = False

    # ... (Keep your existing nmap and ping methods here) ...

    def listen(self, *args):
        """listen function

        Spins up a non-blocking background thread to listen for real chat
        messages.
        Format: listen <port>
        """
        if len(args) < 2:
            print("listen: missing port number")
            return

        if self.listening:
            print("Server is already running and listening.")
            return

        port = int(args[1])

        # To keep the GUI responsive, we spawn a completely separate thread
        # that handles the blocking server loop in the background.
        server_thread = threading.Thread(
            target=self._background_listener, args=(port,), daemon=True
        )
        server_thread.start()

    def _background_listener(self, port):
        """Private Helper: Runs silently in the background to handle inbound

        messages.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind(("0.0.0.0", port))
            self.server_socket.listen(5)
            self.listening = True
            print(
                f"\n[CHAT SERVER] Started successfully. Listening on port {port}..."
            )

            while self.listening:
                # accept() blocks, but since it's on a thread, the GUI stays smooth!
                client_sock, addr = self.server_socket.accept()

                # Read the incoming chat string message packet
                message = client_sock.recv(1024).decode("utf-8")

                # Print it to the screen (Redirector will cleanly catch this and put it in the box)
                print(f"\n[INBOUND CHAT from {addr[0]}]: {message}")

                # Auto-reply confirmation handshake to client
                client_sock.send("ACK: Message delivered.".encode("utf-8"))
                client_sock.close()

        except Exception as e:
            # Silently catch the error thrown when the server is intentionally closed on shutdown
            if self.listening:
                print(f"\n[CHAT SERVER ERROR]: {e}")
        finally:
            self.listening = False

    def send_msg(self, *args):
        """send_msg function

        Connects to another terminal instance running 'listen' and sends text.
        Format: send_msg <ip> <port> <message_text>
        """
        if len(args) < 4:
            print("Usage: send_msg <ip> <port> <message text>")
            return

        target_ip = args[1]
        target_port = int(args[2])

        # Take all arguments after the port and join them back into a single sentence
        chat_text = " ".join(args[3:])

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(4.0)  # Don't hang forever if target is offline

        try:
            client_socket.connect((target_ip, target_port))
            # Encode strings to bytes before pushing through the connection pipeline
            client_socket.send(chat_text.encode("utf-8"))

            # Capture back the acknowledgment check message
            response = client_socket.recv(1024).decode("utf-8")
            print(f"[SYSTEM]: {response}")

        except Exception as e:
            print(f"Chat failed to deliver: {e}")
        finally:
            client_socket.close()

    def stop_listen(self, *args):
        """ stop_listen function
            Gracefully shuts down the background chat server and closes the open port.

            Format:
            >stop_listen
        """
        if not self.listening:
            print("No active server is currently running.")
            return

        print("\n[CHAT SERVER] Shutting down background server...")
        # 1. Flip the loop flag to False so the thread stops looping
        self.listening = False

        # 2. Forcefully close the socket to release the port from your firewall
        if self.server_socket:
            try:
                # This breaks any active accept() block instantly
                self.server_socket.close()
            except Exception:
                pass
        print("[CHAT SERVER] Port released. Connection securely ended.\n")


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
            Checks if a target host is responsive via a specific TCP port.

            Format:
            >ping <ip_or_domain>          : Pings target on default port 445
            >ping <ip_or_domain> -p <port>: Pings target on a custom port
        """
        if len(args) < 2:
            print("ping: missing target operand")
            return

        target = args[1]

        # 1. Establish the default fallback port (445 is great for local Windows machines)
        port = 445

        # 2. Check if the user specified the custom port flag '-p'
        if "-p" in args:
            try:
                # Find where '-p' is in the arguments list
                flag_index = args.index("-p")
                # The actual port number should be the very next item in the tuple
                port = int(args[flag_index + 1])
            except (ValueError, IndexError):
                print("ping: error parsing custom port. Using default port 445 instead.")
                port = 445

        print(f"\nPING {target} on TCP port {port}:")

        success_count = 0
        total_time = 0

        # Run 4 ping cycles
        for i in range(4):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.5)

            start_time = time.perf_counter()

            try:
                result = s.connect_ex((target, port))
                end_time = time.perf_counter()

                latency = (end_time - start_time) * 1000

                # 0 = Connection Open, 10061 = Connection Refused (But host is still alive!)
                if result == 0 or result == 10061:
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
