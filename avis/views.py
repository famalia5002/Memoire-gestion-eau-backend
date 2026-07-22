from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import Avis
from .serializers import AvisSerializer

class ListeAvisView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvisSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'client':
            return Avis.objects.filter(client=user)
        return Avis.objects.all()

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

class DetailAvisView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvisSerializer
    queryset = Avis.objects.all()
