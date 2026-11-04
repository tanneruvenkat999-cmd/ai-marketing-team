"""Seven role agents; Python 3.10+, standard library only."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parent

def generate(instructions, context, model):
    key = os.environ.get('OPENAI_API_KEY')
    if not key:
        raise ValueError('Set OPENAI_API_KEY for live mode, or use --demo.')
    payload = {'model': model, 'instructions': instructions,
               'input': json.dumps(context), 'store': False}
    request = urllib.request.Request('https://api.openai.com/v1/responses',
        data=json.dumps(payload).encode(), headers={
            'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f'AI API returned HTTP {exc.code}; check model access, key and quota.') from None
    if result.get('status') != 'completed':
        raise RuntimeError('AI response did not complete; no completed deliverable recorded.')
    text = '\n'.join(c['text'] for item in result.get('output', [])
                     for c in item.get('content', []) if c.get('type') == 'output_text')
    if not text.strip():
        raise RuntimeError('AI returned no text.')
    return text

def digest(folder):
    h = hashlib.sha256()
    for f in sorted(folder.glob('*.md')):
        h.update(f.name.encode()); h.update(f.read_bytes())
    h.update((folder / 'brief.json').read_bytes())
    return h.hexdigest()

def run(brief_path, folder, demo=False, model=None):
    brief = json.loads(Path(brief_path).read_text())
    if not isinstance(brief, dict) or not brief.get('business_name') or not brief.get('goal'):
        raise ValueError('Brief requires business_name and goal.')
    if not demo and not model:
        raise ValueError('Supply --model with a Responses-compatible model available to your account.')
    if not demo and not os.environ.get('OPENAI_API_KEY'):
        raise ValueError('Set OPENAI_API_KEY before running live mode.')
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    (folder / 'brief.json').write_text(json.dumps(brief, indent=2))
    roster = json.loads((ROOT / 'team.json').read_text())
    context = {'brief': brief, 'drafts': {}}
    with (folder / 'tasks.csv').open('w', newline='') as file:
        ledger = csv.writer(file); ledger.writerow(['owner', 'status', 'file'])
        for index, agent in enumerate(roster, 1):
            name = agent['id']
            print(f"{index}/7: {agent['name']}", flush=True)
            instructions = (ROOT / 'agents' / f'{name}.md').read_text()
            if demo:
                output = (f"# DEMO ONLY — {agent['name']}\n\n"
                          'This is an offline workflow placeholder, not AI-generated marketing work.\n\n'
                          f"Business: {brief['business_name']}\nGoal: {brief['goal']}\n\n"
                          '## Assigned responsibility\n'+instructions.split('\n\n')[-1]+
                          '\n## Status\nNeeds live generation and human review. No external actions taken.\n')
            else:
                output = generate(instructions, context, model)
            filename = f'{index:02d}_{name}.md'
            (folder / filename).write_text(output)
            context['drafts'][name] = output
            ledger.writerow([name, 'demo_placeholder' if demo else 'draft_needs_review', filename])
            file.flush()
    (folder / 'review.json').write_text(json.dumps({
        'status': 'awaiting_human_review', 'demo': demo,
        'package_sha256': digest(folder), 'external_actions_executed': [],
        'integrations': 'not_connected'}, indent=2))
    return folder

def approve(folder, reviewer, scope):
    folder = Path(folder)
    review = json.loads((folder / 'review.json').read_text())
    if review['demo']:
        raise ValueError('Demo placeholders cannot be approved.')
    if review['package_sha256'] != digest(folder):
        raise ValueError('Package changed since generation. Re-run and review the new package.')
    if not reviewer.strip():
        raise ValueError('Reviewer name is required.')
    approval = {'reviewer': reviewer, 'scope': scope, 'package_sha256': digest(folder),
                'status': 'human_review_recorded', 'execution': 'manual_only'}
    (folder / 'approval.json').write_text(json.dumps(approval, indent=2))
    print('Review recorded. No post, email or paid advertisement has been executed.')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    r = sub.add_parser('run')
    r.add_argument('--brief', default=str(ROOT / 'brief.example.json'))
    r.add_argument('--out', required=True)
    r.add_argument('--demo', action='store_true')
    r.add_argument('--model')
    a = sub.add_parser('approve')
    a.add_argument('folder'); a.add_argument('--reviewer', required=True)
    a.add_argument('--scope', choices=['strategy', 'content'], required=True)
    args = parser.parse_args()
    try:
        if args.command == 'run':
            print(run(args.brief, args.out, args.demo, args.model))
        else:
            approve(args.folder, args.reviewer, args.scope)
    except (ValueError, OSError, RuntimeError) as exc:
        parser.exit(1, f'Error: {exc}\n')

if __name__ == '__main__':
    main()
