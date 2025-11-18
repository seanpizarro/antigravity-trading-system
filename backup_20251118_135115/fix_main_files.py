#!/usr/bin/env python3
"""
Emergency fix for 'Opportunity' object has no attribute 'get' error
Following copilot-instructions.md: DeepSeek returns dataclasses, not dicts
"""
import re
from pathlib import Path
from datetime import datetime

def fix_opportunity_access(filepath: Path):
    """Fix .get() calls on Opportunity dataclass objects"""
    print(f"\n📄 Fixing: {filepath}")
    print("-"*80)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = []
    
    # Dataclass variables that shouldn't use .get()
    dataclass_vars = ['opportunity', 'opp', 'decision', 'assessment', 'metrics', 'position']
    
    # Fix 1: opportunity['field'] → opportunity.field
    for var in dataclass_vars:
        pattern = rf"\b({var})\['(\w+)'\]"
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        for match in reversed(matches):
            var_name, field = match.groups()
            old = match.group(0)
            new = f"{var_name}.{field}"
            start, end = match.span()
            content = content[:start] + new + content[end:]
            line_num = original[:start].count('\n') + 1
            changes.append(f"  Line {line_num}: {old} → {new}")
    
    # Fix 2: opportunity.get('field') → opportunity.field
    for var in dataclass_vars:
        pattern = rf"\b({var})\.get\('(\w+)'\)"
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        for match in reversed(matches):
            var_name, field = match.groups()
            old = match.group(0)
            new = f"{var_name}.{field}"
            start, end = match.span()
            content = content[:start] + new + content[end:]
            line_num = original[:start].count('\n') + 1
            changes.append(f"  Line {line_num}: {old} → {new}")
    
    # Fix 3: opportunity.get('field', default) → getattr(opportunity, 'field', default)
    for var in dataclass_vars:
        pattern = rf"\b({var})\.get\('(\w+)',\s*([^)]+)\)"
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        for match in reversed(matches):
            var_name, field, default = match.groups()
            old = match.group(0)
            new = f"getattr({var_name}, '{field}', {default})"
            start, end = match.span()
            content = content[:start] + new + content[end:]
            line_num = original[:start].count('\n') + 1
            changes.append(f"  Line {line_num}: {old} → {new}")
    
    if changes:
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = filepath.with_suffix(f'.backup.{timestamp}.py')
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original)
        
        # Write fixed content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Backup: {backup_path}")
        print(f"✅ Fixed {len(changes)} issues:")
        for change in changes[:10]:
            print(change)
        if len(changes) > 10:
            print(f"  ... and {len(changes)-10} more")
        
        return len(changes)
    else:
        print("✅ No issues found")
        return 0

def main():
    """Fix main orchestrator files"""
    print("="*80)
    print("EMERGENCY FIX: 'Opportunity' object has no attribute 'get'")
    print("="*80)
    print("\nFollowing copilot-instructions.md:")
    print("- DeepSeek returns dataclasses (ManagementDecision, Opportunity, RiskAssessment)")
    print("- Never use .get() on dataclass objects")
    print("- Use direct attribute access or getattr()")
    print("="*80)
    
    # Fix all main files
    files_to_fix = [
        'main.py',
        'main_enhanced_paper.py',
        'trade_manager.py',
        'opportunity_scanner.py',
        'risk_monitor.py',
        'personalization.py',
        'dashboard.py',
        'deepseek_analyst.py'
    ]
    
    total_fixes = 0
    files_fixed = []
    
    for filename in files_to_fix:
        filepath = Path(filename)
        if filepath.exists():
            num_fixes = fix_opportunity_access(filepath)
            if num_fixes > 0:
                total_fixes += num_fixes
                files_fixed.append(filename)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if total_fixes == 0:
        print("\n✅ No issues found - all files follow conventions")
    else:
        print(f"\n✅ Fixed {total_fixes} issues across {len(files_fixed)} files:")
        for f in files_fixed:
            print(f"  - {f}")
        
        print("\n📦 Backups created: *.backup.*.py")
        
        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("\n1. Test the fix:")
        print("   python main.py")
        print("\n2. Verify error is gone:")
        print("   'Opportunity' object has no attribute 'get' ← SHOULD BE FIXED")
        print("\n3. If working, commit:")
        print("   git add -u")
        print("   git commit -m 'Fix: Convert all dataclass .get() to attribute access'")
        print("   git push")
        print("\n4. If issues, restore backup:")
        print("   copy <file>.backup.<timestamp>.py <file>.py")
    
    print("="*80)

if __name__ == "__main__":
    main()
