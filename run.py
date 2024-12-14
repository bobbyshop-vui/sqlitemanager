import subprocess
import time
import sys
import threading

# Hàm timeout sẽ dừng script sau 3 giây
def timeout(proc):
    print("Timeout reached, stopping script...")
    proc.terminate()  # Dừng quá trình đã được tạo bởi subprocess
    sys.exit(1)

# Tạo và chạy quá trình con
proc = subprocess.Popen(["python", "main.py"])

# Tạo một thread để chạy hàm timeout sau 3 giây
timer = threading.Timer(3.0, timeout, [proc])
timer.start()

# Chờ quá trình con hoàn thành
proc.communicate()

# Hủy timer sau khi quá trình hoàn thành
timer.cancel()
