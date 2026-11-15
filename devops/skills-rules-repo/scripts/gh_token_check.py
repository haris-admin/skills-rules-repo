#!/usr/bin/env python3
"""Read-only GitHub token health check. Never prints token values.

Usage: python3 gh_token_check.py [ENV_FILE] [TOKEN_KEY] [REPO]
Defaults: /mnt/c/Users/habib/.hermes/.env GITHUB_PAT_CLASSIC_OPERATOR_AGENT haris-admin/skills-rules-repo
"""
import os, sys, json, urllib.request, urllib.error

def load_env(path):
    env = {}
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, _, v = line.partition('=')
                env[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return env

def api(url, tok):
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'token {tok}')
    req.add_header('Accept', 'application/vnd.github+json')
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, dict(r.headers), json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, dict(e.headers), json.loads(e.read().decode())
        except Exception:
            return e.code, dict(e.headers), {}

env_file = sys.argv[1] if len(sys.argv) > 1 else '/mnt/c/Users/habib/.hermes/.env'
tok_key = sys.argv[2] if len(sys.argv) > 2 else 'GITHUB_PAT_CLASSIC_OPERATOR_AGENT'
repo = sys.argv[3] if len(sys.argv) > 3 else 'haris-admin/skills-rules-repo'

token = load_env(env_file).get(tok_key, '')
print('=' * 60)
if not token:
    print(f'{tok_key}: MISSING (empty)')
    raise SystemExit(1)
print(f'{tok_key}: PRESENT ({len(token)} chars)')

status, headers, body = api('https://api.github.com/user', token)
if status == 200:
    print(f'\n[1] AUTH: OK — login={body.get("login")} name={body.get("name")}')
    print(f'    scopes: {headers.get("X-OAuth-Scopes", "")}')
else:
    print(f'\n[1] AUTH: FAILED ({status}) — {body.get("message", "")}')
    print('=' * 60)
    raise SystemExit(1)

status, headers, body = api(f'https://api.github.com/repos/{repo}', token)
if status == 200:
    p = body.get('permissions', {})
    print(f'[2] REPO {repo}: push={p.get("push")} admin={p.get("admin")} pull={p.get("pull")}')
    print(f'    private={body.get("private")} default_branch={body.get("default_branch")}')
else:
    print(f'[2] REPO ACCESS: FAILED ({status}) — {body.get("message", "")}')

status, headers, body = api(f'https://api.github.com/repos/{repo}/git/refs/heads/main', token)
if status == 200:
    print(f'[3] WRITE PATH: OK — main ref accessible (sha={body.get("object", {}).get("sha", "")[:8]})')
else:
    print(f'[3] WRITE PATH: FAILED ({status}) — {body.get("message", "")}')

print('\n' + '=' * 60)
print('VERDICT: TOKEN ' + ('WORKING, CAN PUSH' if status == 200 else 'NOT AUTHORIZED FOR PUSH'))
