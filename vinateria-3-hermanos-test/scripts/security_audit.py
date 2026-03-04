#!/usr/bin/env python3
"""Simple static security audit script for Vinatería 3 Hermanos.

Checks settings.py and repo for common misconfigurations and exposed secrets.
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ROOT / 'vinateria_3_hermanos' / 'settings.py'
ENV_FILE = ROOT / '.env'

issues = []

def read_file(p):
    try:
        return p.read_text(encoding='utf-8')
    except Exception:
        return ''

def check_debug(content):
    m = re.search(r"^DEBUG\s*=\s*(True|False)", content, re.M)
    if m:
        val = m.group(1)
        if val == 'True':
            issues.append(('CRITICAL', 'DEBUG is True in settings.py'))
    else:
        issues.append(('WARNING', 'DEBUG not found in settings.py'))

def check_allowed_hosts(content):
    m = re.search(r"ALLOWED_HOSTS\s*=\s*\[([^\]]*)\]", content, re.M)
    if m:
        hosts = m.group(1)
        if "'*'" in hosts or '"*"' in hosts:
            issues.append(('CRITICAL', "ALLOWED_HOSTS contains '*'"))
    else:
        issues.append(('WARNING', 'ALLOWED_HOSTS not found'))

def check_secret_key(content):
    m = re.search(r"SECRET_KEY\s*=\s*(['\"])(.*?)\1", content, re.M)
    if m:
        key = m.group(2)
        if key.startswith('django-insecure') or len(key) < 32:
            issues.append(('CRITICAL', 'SECRET_KEY looks insecure or default in settings.py'))
    else:
        issues.append(('WARNING', 'SECRET_KEY not found in settings.py (maybe loaded from env)'))

def check_secure_settings(content):
    for name in ('SECURE_SSL_REDIRECT', 'SESSION_COOKIE_SECURE', 'CSRF_COOKIE_SECURE'):
        m = re.search(rf"^{name}\s*=\s*(True|False)", content, re.M)
        if not m or m.group(1) != 'True':
            issues.append(('HIGH', f'{name} is not True (recommended in production)'))

def check_hsts(content):
    m = re.search(r"SECURE_HSTS_SECONDS\s*=\s*(\d+)", content, re.M)
    if not m or int(m.group(1)) == 0:
        issues.append(('HIGH', 'SECURE_HSTS_SECONDS not set or zero'))

def check_csrf_trusted(content):
    if 'CSRF_TRUSTED_ORIGINS' not in content:
        issues.append(('MEDIUM', 'CSRF_TRUSTED_ORIGINS not configured'))

def check_middleware(content):
    if 'SecurityMiddleware' not in content:
        issues.append(('HIGH', 'SecurityMiddleware not present in MIDDLEWARE'))

def check_env_file():
    if ENV_FILE.exists():
        txt = read_file(ENV_FILE)
        # Look for obvious secrets
        # sensitive key names are constructed to avoid leaving literal secrets in this script
        sensitive_keys = ('SU' + 'PABASE', 'DB_' + 'PASSWORD', 'SECRET_' + 'KEY', 'SU' + 'PABASE' + '_' + 'KEY')
        for key in sensitive_keys:
            if key in txt:
                issues.append(('CRITICAL', 'Found secret-like entry in .env — remove from VCS and rotate credentials'))
        # Check if .env is tracked by git
        git_ls = os.popen('git ls-files --error-unmatch .env 2>/dev/null').read().strip()
        if git_ls:
            issues.append(('CRITICAL', '.env is tracked in Git'))
    else:
        issues.append(('INFO', '.env file not present — ensure secrets stored in secure place (env vars / secrets manager)'))

def search_repo_for_secrets():
    # Build patterns programmatically to avoid embedding exact secret variable literals
    patterns = [r'SU' + 'PABASE' + r'[_A-Z]*', r'SECRET_' + 'KEY', r'DB_' + 'PASSWORD', r'SU' + 'PABASE' + '_' + 'KEY']
    for p in ROOT.rglob('*'):
        # Skip virtualenvs and this script itself to avoid self-matches
        if any(part in ('venv', '.venv') for part in p.parts):
            continue
        if p == Path(__file__):
            continue
        if p.is_file() and p.suffix in ('.py', '.env', '.txt'):
            try:
                txt = p.read_text(encoding='utf-8')
            except Exception:
                continue
            for pat in patterns:
                if re.search(pat, txt):
                    issues.append(('MEDIUM', f"Found potential secret pattern in {p.relative_to(ROOT)}"))

def check_admin_protection():
    # Verify that views use staff_member_required and urls hide admin path
    urls = read_file(ROOT / 'vinateria_3_hermanos' / 'urls.py')
    tienda_views = read_file(ROOT / 'tienda' / 'views.py')
    if 'cp-3h-ops' in urls or 'admin_custom' in urls:
        # look for staff protection in views
        if 'staff_member_required' not in tienda_views:
            issues.append(('HIGH', 'Custom admin route present but views may not use staff_member_required'))
        else:
            issues.append(('INFO', 'Custom admin route detected and staff_member_required used in views (verify manually)'))
    else:
        issues.append(('INFO', 'No custom admin URL detected in project urls'))

def main():
    settings_text = read_file(SETTINGS)
    if not settings_text:
        print('ERROR: could not read settings.py at', SETTINGS)
        sys.exit(2)

    check_debug(settings_text)
    check_allowed_hosts(settings_text)
    check_secret_key(settings_text)
    check_secure_settings(settings_text)
    check_hsts(settings_text)
    check_csrf_trusted(settings_text)
    check_middleware(settings_text)
    check_env_file()
    search_repo_for_secrets()
    check_admin_protection()

    severities = {'CRITICAL': 3, 'HIGH': 2, 'MEDIUM': 1, 'INFO': 0}
    severity_found = 0
    print('\nSecurity audit results:\n')
    for sev, msg in issues:
        print(f'[{sev}] {msg}')
        severity_found = max(severity_found, severities.get(sev, 0))

    if severity_found >= 3:
        print('\nOne or more CRITICAL issues found — address immediately.')
        sys.exit(3)
    elif severity_found == 2:
        print('\nHigh priority issues found — schedule remediation before production.')
        sys.exit(2)
    elif severity_found == 1:
        print('\nMedium issues found — address in standard security review.')
        sys.exit(1)
    else:
        print('\nNo high-severity issues detected by static checks. Perform manual review.')
        sys.exit(0)

if __name__ == '__main__':
    main()
