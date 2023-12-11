from flask import Flask, request, jsonify
import json
import threading
import time
import sort

app = Flask(__name__)

class InputPayload:
    def __init__(self, to_sort):
        self.to_sort = to_sort

class Response:
    def __init__(self, sorted_arrays, time_ns):
        self.sorted_arrays = sorted_arrays
        self.time_ns = time_ns

def process_single(input_list):
    return sorted(input_list)

def process_concurrent(input_list):
    sorted_list = input_list.copy()
    sorted_list.sort()
    return sorted_list

def handle_process_single(payload):
    start_time = time.time()
    sorted_arrays = [process_single(arr) for arr in payload.to_sort]
    time_taken = int((time.time() - start_time) * 1e9)

    response = Response(sorted_arrays=sorted_arrays, time_ns=time_taken)
    return response.__dict__

def handle_process_concurrent(payload):
    start_time = time.time()
    sorted_arrays = []

    def sort_thread(input_list):
        sorted_arrays.append(process_concurrent(input_list))

    threads = [threading.Thread(target=sort_thread, args=(arr,)) for arr in payload.to_sort]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    time_taken = int((time.time() - start_time) * 1e9)

    response = Response(sorted_arrays=sorted_arrays, time_ns=time_taken)
    return response.__dict__

@app.route("/process-single", methods=["POST"])
def api_process_single():
    payload_data = json.loads(request.data.decode("utf-8"))
    payload = InputPayload(**payload_data)
    result = handle_process_single(payload)
    return jsonify(result)

@app.route("/process-concurrent", methods=["POST"])
def api_process_concurrent():
    payload_data = json.loads(request.data.decode("utf-8"))
    payload = InputPayload(**payload_data)
    result = handle_process_concurrent(payload)
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=8000)
