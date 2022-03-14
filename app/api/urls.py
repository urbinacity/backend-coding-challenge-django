from django.urls import path, include
from rest_framework import routers

from api.views import NotesViewset, PublicNotesView, UserCreateView


router = routers.DefaultRouter()
router.register('notes', NotesViewset, 'notes-user')

urlpatterns = [
    path('users/', UserCreateView.as_view(), name='auth-user'),
    path('notes/public/', PublicNotesView.as_view(), name='notes-list-public'),
    path('notes/tags/<str:key>/', NotesViewset.as_view({'get': 'tag_filter'}), name='notes-list-public'),
    path('', include(router.urls)),
]
