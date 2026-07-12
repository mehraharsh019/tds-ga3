import json
import functools

# Change this filename if your actual file is named differently.
DATASET_FILE = 'q-cosine-similarity-server.json'

# Tie-break rule: if two documents have equal similarity, the one with the smaller doc_id comes first.
def cmp(a, b):
    # Use a small epsilon for floating point comparison
    if abs(a['sim'] - b['sim']) > 1e-12:
        return -1 if a['sim'] > b['sim'] else 1
    
    # Tie-breaker by doc_id (lexicographical)
    return -1 if a['id'] < b['id'] else (1 if a['id'] > b['id'] else 0)

def main():
    try:
        with open(DATASET_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {DATASET_FILE} not found. Please make sure the file is in the same folder.")
        return

    docs = data['documents']
    queries = data['queries']
    res = {}

    for q in queries:
        sims = []
        for doc in docs:
            # Compute full cosine similarity: dot(A, B) / (norm(A) * norm(B))
            dot_product = sum(q['embedding'][k] * doc['embedding'][k] for k in range(len(q['embedding'])))
            
            import math
            norm_q = math.sqrt(sum(val * val for val in q['embedding']))
            norm_doc = math.sqrt(sum(val * val for val in doc['embedding']))
            
            # Avoid division by zero
            if norm_q == 0 or norm_doc == 0:
                cosine_sim = 0
            else:
                cosine_sim = dot_product / (norm_q * norm_doc)
                
            sims.append({'id': doc['doc_id'], 'sim': cosine_sim})
            
        # Sort using the comparison function
        sims.sort(key=functools.cmp_to_key(cmp))
        
        # Take the top 5 document IDs
        res[q['query_id']] = [x['id'] for x in sims[:5]]

    # Output the exact single-line JSON format required by the grader
    print(json.dumps(res))

if __name__ == '__main__':
    main()