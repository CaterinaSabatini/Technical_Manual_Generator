import requests
import subprocess
import time

"""
Starts and manages the Ollama process.
@param ollama_path: Path to the Ollama executable.
@param healthcheck_url: URL to check if Ollama is ready.
@param max_retries: Maximum number of retries for health checks.
@param retry_delay: Delay between retries in seconds.
@param request_timeout: Timeout for each health check request in seconds.
@return: The subprocess.Popen object representing the Ollama process.
"""
def start_ollama(ollama_path, healthcheck_url, max_retries, retry_delay, request_timeout):
    process = subprocess.Popen(
        [ollama_path, "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for attempt in range(1, max_retries + 1):

        # Check if the process crashed
        if process.poll() is not None:
            raise RuntimeError("Ollama process exited during startup")

        try:
            response = requests.get(
                healthcheck_url,
                timeout=request_timeout,
            )
            response.raise_for_status()
            print(f"Ollama is ready (attempt {attempt}/{max_retries})", flush=True)
            return process

        except requests.RequestException as e:
            print(f"Attempt {attempt}/{max_retries}: Waiting for Ollama... ({type(e).__name__})", flush=True)
            time.sleep(retry_delay)

    raise TimeoutError("Ollama did not become available in time")

"""
Terminates the Ollama process.
@param process: The subprocess.Popen object representing the Ollama process.
@return: None
"""
def stop_ollama(process):

    if process is None:
        return

    if process.poll() is not None:
        print("Ollama process terminated.", flush=True)
        return

    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        print("Ollama process killed.", flush=True)


     