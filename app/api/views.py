from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.models import Note
from api.serializers import NoteSerializer, UserSerializer


class NotesViewset(ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(created_by=self.request.user).all()

    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(Note.objects.filter(
            Q(private=False) | Q(created_by=self.request.user.pk)
        ), **kwargs)
        serializer = NoteSerializer(instance)
        return Response(serializer.data)

    def tag_filter(self, request, *args, **kwargs):
        instance = Note.objects.filter(
            Q(private=False) | Q(created_by=self.request.user.pk)
        ).filter(
            tags__title__iexact=kwargs.get('key')
        ).all()
        serializer = NoteSerializer(instance, many=True)
        return Response(serializer.data)

class PublicNotesView(ListAPIView):
    serializer_class = NoteSerializer

    def get_queryset(self):
        return Note.objects.filter(private=False).all()

class UserCreateView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
