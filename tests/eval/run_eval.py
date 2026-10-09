import json
import time
import requests

API_URL = "http://localhost:8000/api"

def run_eval():
    with open("tests/eval/eval_queries.json", "r") as f:
        queries = json.load(f)
        
    correct_routes = 0
    total = len(queries)
    latencies = []
    
    print("Running Eval...")
    for q in queries:
        print(f"\nQuery: {q['query']}")
        start = time.time()
        try:
            res = requests.post(f"{API_URL}/chat", json={"message": q['query']}).json()
            route = res.get("route")
            answer = res.get("answer", "").lower()
            latencies.append(time.time() - start)
            
            route_match = route == q["expected_route"] or (q["expected_route"] in route)
            kw_match = all(kw.lower() in answer for kw in q["expected_keywords"])
            
            if route_match: correct_routes += 1
            print(f"Expected Route: {q['expected_route']} | Got: {route} -> {'PASS' if route_match else 'FAIL'}")
            print(f"Keywords Match: {'PASS' if kw_match else 'FAIL'}")
        except Exception as e:
            print(f"Error: {e}")
            
    print(f"\nRoute Accuracy: {correct_routes/total*100}%")
    if latencies:
        print(f"Avg Latency: {sum(latencies)/len(latencies):.2f}s")

if __name__ == "__main__":
    run_eval()
