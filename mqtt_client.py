import paho.mqtt.client as mqtt
import json
import django
import os
import ssl
 
# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backendMemoire.settings')
django.setup()
 
# Configuration MQTT
MQTT_HOST = 'y8182a1b.ala.eu-central-1.emqxsl.com'
MQTT_PORT = 8883
MQTT_USERNAME = 'django'
MQTT_PASSWORD = 'Django@2026'
 
# Topics
TOPIC_CONSOMMATION = 'smartndiyam/consommation'
TOPIC_VANNE_STATUT = 'smartndiyam/vanne/statut'
TOPIC_ALERTE = 'smartndiyam/alerte'
TOPIC_VANNE_CMD = 'smartndiyam/vanne/cmd'
 
 
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("✅ Connecté au broker MQTT EMQX Cloud !")
        client.subscribe(TOPIC_CONSOMMATION)
        client.subscribe(TOPIC_VANNE_STATUT)
        client.subscribe(TOPIC_ALERTE)
        print(f"📡 Souscrit aux topics :")
        print(f"   - {TOPIC_CONSOMMATION}")
        print(f"   - {TOPIC_VANNE_STATUT}")
        print(f"   - {TOPIC_ALERTE}")
    else:
        print(f"❌ Erreur connexion MQTT : code {reason_code}")
 
 
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    print(f"\n📨 Message reçu sur {topic}: {payload}")
 
    try:
        data = json.loads(payload)
 
        # ===== CONSOMMATION =====
        if topic == TOPIC_CONSOMMATION:
            handle_consommation(data)
 
        # ===== STATUT VANNE =====
        elif topic == TOPIC_VANNE_STATUT:
            handle_vanne_statut(data)
 
        # ===== ALERTE =====
        elif topic == TOPIC_ALERTE:
            handle_alerte(data)
 
    except json.JSONDecodeError:
        print(f"❌ Erreur JSON: {payload}")
    except Exception as e:
        print(f"❌ Erreur traitement: {e}")
 
 
def handle_consommation(data):
    """Enregistrer la consommation depuis ESP32"""
    from compteurs.models import Compteur
    from consommation.models import Consommation, Index
 
    try:
        numero_compteur = data.get('numero_compteur')
        volume = float(data.get('volume', 0))
 
        print(f"💧 Consommation reçue : {volume} L pour compteur {numero_compteur}")
 
        # Trouver le compteur
        compteur = Compteur.objects.get(numero_compteur=numero_compteur)
 
        # Créer la consommation
        Consommation.objects.create(
            compteur=compteur,
            volume=volume
        )
 
        # Mettre à jour l'index
        dernier_index = Index.objects.filter(
            compteur=compteur
        ).order_by('-date_releve').first()
 
        nouvelle_valeur = (
            dernier_index.valeur_index if dernier_index else 0
        ) + (volume / 1000)
 
        Index.objects.create(
            compteur=compteur,
            valeur_index=round(nouvelle_valeur, 4)
        )
 
        print(f"✅ Consommation enregistrée : {volume} L - Index : {nouvelle_valeur} m³")
 
    except Compteur.DoesNotExist:
        print(f"❌ Compteur {numero_compteur} non trouvé")
    except Exception as e:
        print(f"❌ Erreur consommation: {e}")
 
 
def handle_vanne_statut(data):
    """Mettre à jour le statut de la vanne"""
    from compteurs.models import Compteur
 
    try:
        numero_compteur = data.get('numero_compteur')
        etat = data.get('etat')  # 'ouverte' ou 'fermee'
 
        compteur = Compteur.objects.get(numero_compteur=numero_compteur)
        compteur.etat_vanne = etat
        compteur.save()
 
        print(f"✅ Vanne {numero_compteur} : {etat}")
 
    except Compteur.DoesNotExist:
        print(f"❌ Compteur {numero_compteur} non trouvé")
    except Exception as e:
        print(f"❌ Erreur vanne statut: {e}")
 
 
def handle_alerte(data):
    """Créer une alerte depuis ESP32"""
    from compteurs.models import Compteur
    from alertes.models import Alerte
 
    try:
        numero_compteur = data.get('numero_compteur')
        type_alerte = data.get('type_alerte', 'autre')
 
        compteur = Compteur.objects.get(numero_compteur=numero_compteur)
 
        # Vérifier si alerte déjà en cours
        alerte_existante = Alerte.objects.filter(
            compteur=compteur,
            type_alerte=type_alerte,
            statut='en_cours'
        ).first()
 
        if not alerte_existante:
            Alerte.objects.create(
                compteur=compteur,
                type_alerte=type_alerte,
                statut='en_cours'
            )
            print(f"⚠️ Alerte créée : {type_alerte} pour {numero_compteur}")
        else:
            print(f"⚠️ Alerte {type_alerte} déjà en cours pour {numero_compteur}")
 
    except Compteur.DoesNotExist:
        print(f"❌ Compteur {numero_compteur} non trouvé")
    except Exception as e:
        print(f"❌ Erreur alerte: {e}")
 
 
def publier_commande_vanne(client, numero_compteur, action):
    """Publier une commande pour contrôler la vanne"""
    payload = json.dumps({
        'numero_compteur': numero_compteur,
        'action': action  # 'ouvrir' ou 'fermer'
    })
    client.publish(TOPIC_VANNE_CMD, payload)
    print(f"📤 Commande vanne publiée : {action} pour {numero_compteur}")
 
 
def start_mqtt():
    """Démarrer le client MQTT"""
    client = mqtt.Client(
        client_id="django_subscriber",
        protocol=mqtt.MQTTv5,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )
 
    # Configuration TLS
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)
 
    # Authentification
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
 
    # Callbacks
    client.on_connect = on_connect
    client.on_message = on_message
 
    print(f"🔄 Connexion au broker MQTT : {MQTT_HOST}:{MQTT_PORT}")
 
    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_forever()
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
 
 
if __name__ == '__main__':
    start_mqtt()
 