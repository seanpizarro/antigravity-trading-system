# Script: Append session summary to copilot_session_history.md
import datetime
import os

SESSION_FILE = 'copilot_session_history.md'

summary = '''
## Session End: {date}

### Key Actions
- Files edited: {files}
- Commands run: {commands}
- Major decisions: {decisions}
- Next steps: {next_steps}
---
'''

def get_recent_files():
    # List files modified in the last 24 hours
    cutoff = datetime.datetime.now().timestamp() - 24*3600
    files = []
    for root, _, filenames in os.walk('.'):
        for fname in filenames:
            try:
                fpath = os.path.join(root, fname)
                if os.path.isfile(fpath) and os.path.getmtime(fpath) > cutoff:
                    files.append(fpath)
            except Exception:
                pass
    return files

def get_recent_commands():
    # Placeholder: User can manually add commands or parse from terminal logs
    return ['streamlit run web_dashboard.py', 'python validate_system.py']

def main():
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    files = ', '.join(get_recent_files())
    commands = ', '.join(get_recent_commands())
    decisions = 'Summarize major decisions here.'
    next_steps = 'List next steps here.'
    entry = summary.format(date=date, files=files, commands=commands, decisions=decisions, next_steps=next_steps)
    with open(SESSION_FILE, 'a', encoding='utf-8') as f:
        f.write(entry)
    print(f'Session summary appended to {SESSION_FILE}')

if __name__ == '__main__':
    main()
