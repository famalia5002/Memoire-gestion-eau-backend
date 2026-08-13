from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def envoyer_email_bienvenue(client, password_temporaire):
    """
    Envoie un email de bienvenue au client avec ses identifiants
    """
    try:
        sujet = f"Bienvenue sur Smart Ndiyam - Vos identifiants de connexion"

        # Contexte du template
        context = {
            'prenom': client.first_name,
            'nom': client.last_name,
            'username': client.username,
            'password': password_temporaire,
            'zone': client.zone or 'N/A',
        }

        # Générer le contenu HTML
        html_content = render_to_string(
            'emails/bienvenue_client.html',
            context
        )

        # Contenu texte simple (fallback)
        text_content = f"""
Bonjour {client.first_name} {client.last_name},

Votre demande d'abonnement a été acceptée !

Vos identifiants de connexion :
- Nom d'utilisateur : {client.username}
- Mot de passe temporaire : {password_temporaire}
- Zone : {client.zone or 'N/A'}

Veuillez changer votre mot de passe dès votre première connexion.

Prochaines étapes :
1. Un technicien va contacter pour installer votre compteur.
2. Téléchargez l'application mobile Smart Ndiyam.
3. Connectez-vous avec vos identifiants.
4. Changez votre mot de passe temporaire.

Smart Ndiyam - Système Intelligent de Gestion d'Eau IoT
        """

        # Créer et envoyer l'email
        email = EmailMultiAlternatives(
            subject=sujet,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[client.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        print(f"Email envoyé à {client.email}")
        return True

    except Exception as e:
        print(f"Erreur envoi email : {e}")
        return False