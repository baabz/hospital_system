import re

file_path = r"c:\Users\user\Desktop\galbose\templates\medical_records\prescription_form.html"

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix split template variables - replace multiline patterns with single line versions
# Fix {{ patient.get_gender_display }}
content = re.sub(
    r'\{\{\s*patient\.get_gender_display\s+\}\}',
    '{{ patient.get_gender_display }}',
    content,
    flags=re.DOTALL
)

# Fix {{ patient.allergies }}
content = re.sub(
    r'\{\{\s*patient\.allergies\s+\}\}',
    '{{ patient.allergies }}',
    content,
    flags=re.DOTALL
)

# Fix {% endif %}
content = re.sub(
    r'\{\%\s+endif\s+\%\}',
    '{% endif %}',
    content
)

# Write the file back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("File fixed successfully!")
