import re

with open('landing/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace {{ url_for('static', filename='X') }} with static/X
content = re.sub(
    r"{{\s*url_for\('static',\s*filename='([^']+)'\)\s*}}",
    r'static/\1',
    content
)

# Fix stale tech stack copy
content = content.replace('Supabase Cloud', 'SQLite Local DB')
content = content.replace(
    'Real-time PostgreSQL infrastructure with secure auth and sync.',
    'Local, offline-first SQLite database. No cloud dependency required.'
)

# Fix grammar: "companys" -> "companies"
content = content.replace('their\n                         companys.', 'their\n                         companies.')

with open('landing/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

remaining = re.findall(r'{{.*?}}', content)
if remaining:
    print(f'WARNING: {len(remaining)} Jinja2 tags remaining: {remaining[:5]}')
else:
    print('OK: Static index.html created with no Jinja2 tags.')
