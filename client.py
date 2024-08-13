import asyncio
import subprocess
import sys
import os


# This would be placed on Ubuntu VM. Ensure firewall is not blocking connections.
SERVER_IP = "0.0.0.0" # put your actual server IP here 
SERVER_PORT = 8888  # can put any port here       
LOG_FILE = "/tmp/terminal_session.log"  # Path to log file. But can put anything for log file 

#TO DO: handle errors sending data 
async def send_data(data):
    reader, writer = await asyncio.open_connection(SERVER_IP, SERVER_PORT)
    writer.write(data.encode())
    await writer.drain()  
    writer.close()
    await writer.wait_closed()

async def monitor_log_file(log_file):
    # Create the log file if it does not exist
    if not os.path.exists(log_file):
        with open(log_file, 'w'):
            pass

    buffer = ""
    with open(log_file, 'r') as file:
        while True:
            # Read new data from the log file
            new_data = file.read()
            if new_data:
                buffer += new_data
                # Check if the buffer contains complete lines
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        await send_data(line + '\n')  # Send the complete line
            await asyncio.sleep(1)  

def start_script_command(log_file):
    cmd = ['script', '-q', '-f', log_file] # script command
    process = subprocess.Popen(cmd) # starts script in command line
    return process

def main():
    process = start_script_command(LOG_FILE)
    
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(monitor_log_file(LOG_FILE))
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        process.terminate()
        process.wait()
        loop.stop()
        loop.close()

if __name__ == "__main__":
    main()
