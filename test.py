from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import time
import concurrent.futures

app = FastAPI()

class InputPayload(BaseModel):
    to_sort: List[List[int]]

class Response(BaseModel):
    sorted_arrays: List[List[int]]
    time_ns: int

def process_single(input_list):
    return sorted(input_list)

def process_concurrent(input_list):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return list(executor.map(sorted, input_list))

@app.post("/process-single")
def handle_process_single(payload: InputPayload):
    start_time = time.time()
    sorted_arrays = [process_single(arr) for arr in payload.to_sort]
    time_taken = int((time.time() - start_time) * 1e9)

    response = Response(sorted_arrays=sorted_arrays, time_ns=time_taken)
    return response

@app.post("/process-concurrent")
def handle_process_concurrent(payload: InputPayload):
    start_time = time.time()
    sorted_arrays = process_concurrent(payload.to_sort)
    time_taken = int((time.time() - start_time) * 1e9)

    response = Response(sorted_arrays=sorted_arrays, time_ns=time_taken)
    return response
