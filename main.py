import argparse, os, sys, time, requests, json
MODEL="mistralai/mistral-7b-instruct:free"
ENDPOINT="https://openrouter.ai/api/v1/chat/completions"
def build_prompt(args):
    if not args.tone:
        args.tone="friendly"
    return f"Write five fundraising emails and four social captions for the {args.event} on {args.date} in a {args.tone} tone."
def chat_completion(prompt):
    key=os.getenv("OPENROUTER_API_KEY")
    if not key:
        sys.exit("missing OPENROUTER_API_KEY")
    payload={"model":MODEL,"messages":[{"role":"user","content":prompt}]}
    t0=time.time()
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "Nyla Fundraiser CLI"
    }
    r=requests.post(ENDPOINT, headers=headers, json=payload, timeout=60)
    dt=time.time()-t0
    if r.status_code!=200:
        sys.exit(f"HTTP {r.status_code}: {r.text[:120]}")
    print(f"done in {dt:.2f}s",file=sys.stderr)
    try:
        return r.json()["choices"][0]["message"]["content"]
    except requests.exceptions.JSONDecodeError:
        print(f"Error: Failed to decode JSON response.", file=sys.stderr)
        print(f"Status Code: {r.status_code}", file=sys.stderr)
        print(f"Response Text: {r.text}", file=sys.stderr)
        sys.exit("Exiting due to JSON decoding error.")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--event",default="Community Gala"); p.add_argument("--date",default="TBD"); p.add_argument("--tone",default="upbeat"); p.add_argument("--dry-run",action="store_true")
    a=p.parse_args()
    prompt=build_prompt(a)
    if a.dry_run:
        print(prompt); return
    out=chat_completion(prompt)
    os.makedirs("out",exist_ok=True)
    with open("out/campaign.md","w") as f: f.write(out)
    print(out)
if __name__=="__main__":
    main()
