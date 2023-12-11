package main

import (
	"encoding/json"
	"net/http"
	"sort"
	"sync"
	"time"
)

type InputPayload struct {
	ToSort [][]int `json:"to_sort"`
}

type Response struct {
	SortedArrays [][]int `json:"sorted_arrays"`
	TimeNS       string  `json:"time_ns"`
}

func processSingle(input []int) []int {
	sort.Ints(input)
	return input
}

func processConcurrent(input []int) []int {
	var wg sync.WaitGroup
	wg.Add(1)

	go func() {
		sort.Ints(input)
		wg.Done()
	}()

	wg.Wait()
	return input
}

func handleProcessSingle(w http.ResponseWriter, r *http.Request) {
	var payload InputPayload
	err := json.NewDecoder(r.Body).Decode(&payload)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	startTime := time.Now()
	var sortedArrays [][]int
	for _, arr := range payload.ToSort {
		sortedArrays = append(sortedArrays, processSingle(arr))
	}
	timeTaken := time.Since(startTime).Nanoseconds()

	response := Response{
		SortedArrays: sortedArrays,
		TimeNS:       timeTaken,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func handleProcessConcurrent(w http.ResponseWriter, r *http.Request) {
	var payload InputPayload
	err := json.NewDecoder(r.Body).Decode(&payload)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	startTime := time.Now()
	var sortedArrays [][]int
	var wg sync.WaitGroup

	for _, arr := range payload.ToSort {
		wg.Add(1)
		go func(input []int) {
			defer wg.Done()
			sortedArrays = append(sortedArrays, processConcurrent(input))
		}(arr)
	}

	wg.Wait()
	timeTaken := time.Since(startTime).Nanoseconds()

	response := Response{
		SortedArrays: sortedArrays,
		TimeNS:       timeTaken,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/process-single", handleProcessSingle)
	http.HandleFunc("/process-concurrent", handleProcessConcurrent)

	http.ListenAndServe(":8000", nil)
}
