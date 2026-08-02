from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentification
    path('connexion/', views.ConnexionView.as_view(), name='connexion'),
    path('deconnexion/', views.DeconnexionView.as_view(), name='deconnexion'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profil
    path('profil/', views.ProfilView.as_view(), name='profil'),
    path('profil/modifier/', views.ModifierProfilView.as_view(), name='modifier_profil'),
    path('profil/photo/', views.ModifierPhotoView.as_view(), name='modifier_photo'),
    path('profil/password/', views.ChangerMotDePasseView.as_view(), name='changer_password'),
    
    # Clients
    path('clients/', views.ListeClientsView.as_view(), name='liste_clients'),
    path('clients/<int:pk>/', views.DetailClientView.as_view(), name='detail_client'),
    
    # Admins zones
    path('admins/', views.ListeAdminsView.as_view(), name='liste_admins'),
    path('admins/<int:pk>/', views.DetailAdminView.as_view(), name='detail_admin'),
]