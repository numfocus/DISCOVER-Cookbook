import os

base_path = 'locales/en/LC_MESSAGES'
resource_prefix = 'numfocus.DISCOVER-Cookbook'  

config_blocks = ["[main]\nhost = https://www.transifex.com\n"]

for filename in os.listdir(base_path):
    if filename.endswith('.po'):
        name = os.path.splitext(filename)[0]
        block = f"""
[{resource_prefix}.{name}]
file_filter = locales/<lang>/LC_MESSAGES/{filename}
source_file = locales/en/LC_MESSAGES/{filename}
source_lang = en
type = PO
"""
        config_blocks.append(block.strip())

with open('.tx/config', 'w') as f:
    f.write('\n\n'.join(config_blocks))
