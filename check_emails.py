import json
 
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
 
emails = {}
doublons = []
 
for obj in data:
    if obj['model'] == 'utilisateurs.utilisateur':
        email = obj['fields'].get('email', '')
        pk = obj['pk']
        username = obj['fields'].get('username', '')
 
        if email in emails:
            doublons.append({
                'email': email,
                'id1': emails[email]['id'],
                'username1': emails[email]['username'],
                'id2': pk,
                'username2': username,
            })
        else:
            emails[email] = {'id': pk, 'username': username}
 
if doublons:
    print(f"Emails dupliques trouves : {len(doublons)}")
    for d in doublons:
        print(f"\nEmail: {d['email']}")
        print(f"  -> ID:{d['id1']} username:{d['username1']}")
        print(f"  -> ID:{d['id2']} username:{d['username2']}")
else:
    print("Aucun email duplique trouve dans data.json !")
    print(f"Total utilisateurs: {len(emails)}")