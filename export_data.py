import os
import django
import io
 
os.environ['DJANGO_SETTINGS_MODULE'] = 'backendMemoire.settings'
django.setup()
 
from django.core import management
 
print("Export des données en cours...")
 
output = io.StringIO()
management.call_command(
    'dumpdata',
    '--exclude', 'auth.permission',
    '--exclude', 'contenttypes',
    '--indent', '2',
    stdout=output
)
 
with open('data.json', 'w', encoding='utf-8') as f:
    f.write(output.getvalue())
 
print("Export réussi ! Fichier data.json créé.")
 