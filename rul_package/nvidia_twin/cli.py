import subprocess
import sys
import os
import time

def main():
    print("========================================")
    print(" Starting E2CC Digital Twin via PIP... ")
    print("========================================")

    # Find where the package is installed so we can locate the files
    base_dir = os.path.dirname(os.path.abspath(__file__))

    gen_path = os.path.join(base_dir, "../data_generator.py")
    ai_path = os.path.join(base_dir, "../full_client.py")
    rul_path = os.path.join(base_dir, "rul_days.py")
    static_path = os.path.join(base_dir, "static", "dist")

    processes = []
    try:
        # 1. Start Python Backends
        print("[1/4] Starting Data Generator...")
        processes.append(subprocess.Popen([sys.executable, gen_path]))

        print("[2/4] Starting AI Engine...")
        processes.append(subprocess.Popen([sys.executable, ai_path]))

        print("[3/4] Starting RUL Calculator...")
        processes.append(subprocess.Popen([sys.executable, rul_path]))

        # 4. Start a built-in Python web server to host the React UI
        print("[4/4] Starting Web Dashboard on Port 8080...")
        processes.append(subprocess.Popen([sys.executable, "-m", "http.server", "8080", "--directory", static_path]))


        print("\nALL SYSTEMS ONLINE! Open http://localhost:8080 in your browser.")
        print("Press CTRL+C to safely shut down all services.")

        # Keep the main process alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down all Digital Twin services...")
        for p in processes:
            p.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()