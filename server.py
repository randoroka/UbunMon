import asyncio
import aiofiles #Not a native Python library, must download
import argparse
from datetime import datetime
import random

log_to_file = False  # Disabled by default
log_to_terminal = False  # Disabled by default
log_file_path = None  #

async def echo(reader, writer):
    log_file = None

    # Open the file in append mode asynchronously with UTF-8 encoding if logging to file is enabled
    if log_to_file and log_file_path:
        log_file = await aiofiles.open(log_file_path, 'a', encoding='utf-8')

    while True:
        data = await reader.read(100)
        if not data:
            break

        # Decode the received data as UTF-8
        message = data.decode('utf-8')
        addr = writer.get_extra_info('peername')

        # Prints data to terminal for real time monitoring 
        if log_to_terminal:
            print(message)

        # formats data by adding newlines
        log_message = message + '\n' if message.strip() else '\n'

        # Write the message to the log file asynchronously if desired
        if log_to_file and log_file:
            await log_file.write(log_message)

    # Close the file if it was opened
    if log_file:
        await log_file.close()

    writer.close()
    await writer.wait_closed()

async def main():
    global log_to_file, log_to_terminal, log_file_path

    parser = argparse.ArgumentParser(description="Run an async server with logging options.")
    parser.add_argument('--terminal', action='store_true', help="Enable printing messages to the terminal.")
    parser.add_argument('--file', nargs='?', type=str, const=None, help="Enable logging messages to a file. Provide filename or leave empty for default.")
    args = parser.parse_args()

    log_to_terminal = args.terminal
    log_to_file = args.file is not None or args.file is None
    log_file_path = args.file if args.file is not None else f"log_{random.randint(100, 999)}.txt" #if a filename is not given, it generates a random one


    if not log_to_terminal and not log_to_file:
        print("Warning: Neither terminal nor file logging is enabled. No logs will be recorded.")
    
    if log_to_file:
        print(f"Logging to file: {log_file_path}")
    #specify Ubuntu IP address to bind to it, or just leave 0.0.0.0 to be open to all interfaces
    server = await asyncio.start_server(echo, "0.0.0.0", 8888)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
