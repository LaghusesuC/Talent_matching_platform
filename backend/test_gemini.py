import os, sys, json, re
# Reads from environment variable or .env file
os.environ.setdefault('GEMINI_API_KEY', os.getenv('GEMINI_API_KEY', ''))
sys.path.insert(0, '.')

import google.generativeai as genai
genai.configure(api_key=os.environ['GEMINI_API_KEY'])
model = genai.GenerativeModel('gemini-3.8-flash')

# Test 1: raw model call
prompt = """Extract skills from this resume text. Return ONLY a JSON object with key "skills" as a list of strings.
Resume: John Doe. Skills: Python, FastAPI, Docker, PostgreSQL, Machine Learning, Git."""

resp = model.generate_content(prompt)
print("=== RAW RESPONSE ===")
print(repr(resp.text[:500]))

# Test 2: our parser
def parse(text):
    fenced = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if fenced:
        try: return json.loads(fenced.group(1))
        except: pass
    try:
        start = text.index('{')
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == '{': depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return json.loads(text[start:i+1])
    except: pass
    return {}

result = parse(resp.text)
print("=== PARSED ===")
print(json.dumps(result, indent=2))
