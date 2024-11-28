import subprocess

# الدالة لتشغيل الأمر بشكل متكرر
def run_command_repeatedly():
    command = 'find . -type f \\( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" \\) -print | xargs -I {} python3 f.py "{}"'
    
    while True:
        try:
            # تشغيل الأمر ومراقبته حتى ينتهي
            result = subprocess.run(command, shell=True, check=True)
            print("Command executed successfully. Re-running the command...")
        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e}. Re-running the command...")

# بدء تشغيل الدالة
if __name__ == "__main__":
    run_command_repeatedly()