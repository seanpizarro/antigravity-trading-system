# save_as: find_typo.py
import re

# Read the dashboard.py file
with open('dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Search for the incorrect import
mime_text_matches = re.findall(r'MimeText', content)
mime_multipart_matches = re.findall(r'MimeMultipart', content)

print("🔍 Searching for typos in dashboard.py...")
print(f"MimeText occurrences: {mime_text_matches}")
print(f"MimeMultipart occurrences: {mime_multipart_matches}")

if mime_text_matches or mime_multipart_matches:
    print("❌ Typos found! Let me fix them...")
    
    # Replace all occurrences
    fixed_content = content.replace('MimeText', 'MIMEText')
    fixed_content = fixed_content.replace('MimeMultipart', 'MIMEMultipart')
    
    # Write the fixed content back
    with open('dashboard.py', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ Fixed all typos in dashboard.py!")
else:
    print("✅ No typos found in dashboard.py")

# Also check if there are any other files with the same issue
import os
other_files = [f for f in os.listdir('.') if f.endswith('.py') and f != 'dashboard.py' and f != 'find_typo.py']

for file in other_files:
    with open(file, 'r', encoding='utf-8') as f:
        file_content = f.read()
    
    if 'MimeText' in file_content or 'MimeMultipart' in file_content:
        print(f"❌ Found typos in {file}")
    else:
        print(f"✅ {file} is clean")