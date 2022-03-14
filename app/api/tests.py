import json

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate

from api.models import Note, Tag
from api.views import NotesViewset, PublicNotesView, UserCreateView

_USER = get_user_model()


# Create your tests here.
USER_CREATE_VIEW_PATH = '/api/users/'
USER_NOTES_VIEW_PATH = '/api/notes/'
USER_NOTES_DETAIL_PATH = '/api/notes/<pk>/'
PUBLIC_NOTES_VIEW_PATH = '/api/notes/public/'
PUBLIC_NOTES_TAG_FILTER_PATH = '/api/notes/public/<key>/'

class TestNotes(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @classmethod
    def setUpClass(cls):
        cls.user_1 = _USER.objects.create_user(**{
            'username': 'test',
            'password': 'test',
            'email': 'test@test.com'
        })
        cls.user_2 = _USER.objects.create_user(**{
            'username': 'fav',
            'password': 'fav',
            'email': 'fav@fav.com'
        })
        cls.note_1_payload = {
            'title': 'Note #1',
            'body': 'I am Lorem Ipsum test note',
            'private': True,
            'tags': [
                {
                    'title': 'hello world',
                },
                {
                    'title': 'lorem ipsum',
                },
                {
                    'title': 'sales',
                },
            ],
        }
        cls.note_2_payload = {
            'title': 'Note #2',
            'body': 'I am Marketing/e-commerce test note',
            'private': True,
            'tags': [
                {
                    'title': 'marketing',
                },
                {
                    'title': 'ecommerce',
                },
                {
                    'title': 'update',
                },
            ],
        }

    @classmethod
    def tearDownClass(cls):
        cls.user_1.delete()

    def create_note(self, payload):
        # create dummy note
        instance = Note(
            title=payload['title'],
            body=payload['body'],
            created_by=self.user_1,
        )
        instance.save()

        # create tags separately
        tags = []
        for tag in payload['tags']:
            obj, created = Tag.objects.get_or_create(title=tag.get('title'))
            tags.append(obj)

        instance.tags.set(tags)
        return instance

    def get_view(self, action):
        if action == 'list':
            return NotesViewset.as_view({'get': 'list'})
        elif action == 'retrieve':
            return NotesViewset.as_view({'get': 'retrieve'})
        elif action == 'create':
            return NotesViewset.as_view({'post': 'create'})
        elif action == 'update':
            return NotesViewset.as_view({'put': 'update'})
        elif action == 'destroy':
            return NotesViewset.as_view({'delete': 'destroy'})
        elif action == 'filter':
            return NotesViewset.as_view({'get': 'tag_filter'})
        elif action == 'public':
            return PublicNotesView.as_view()

    def test_notes_list_authentication(self):
        request = self.factory.get(USER_NOTES_VIEW_PATH)
        response = self.get_view('list')(request)
        self.assertEqual(response.status_code, 401)

    def test_notes_create_authentication(self):
        request = self.factory.post(USER_NOTES_VIEW_PATH)
        response = self.get_view('create')(request)
        self.assertEqual(response.status_code, 401)

    def test_user_notes_list_response(self):
        request = self.factory.get(USER_NOTES_VIEW_PATH)
        force_authenticate(request, user=self.user_1)
        response = self.get_view('list')(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_notes_create_validation(self):
        payload = {
        }
        request = self.factory.post(
            USER_NOTES_VIEW_PATH, json.dumps(payload),
            content_type='application/json'
        )
        force_authenticate(request, user=self.user_1)
        response = self.get_view('create')(request)

        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response.data, dict)
        self.assertEqual(response.data['title'][0].code, 'required')
        self.assertEqual(response.data['body'][0].code, 'required')

    def test_notes_create_success(self):
        payload = self.note_1_payload
        request = self.factory.post(
            USER_NOTES_VIEW_PATH, json.dumps(payload),
            content_type='application/json'
        )
        force_authenticate(request, user=self.user_1)
        response = self.get_view('create')(request)

        self.assertEqual(response.status_code, 201)
        self.assertIsInstance(response.data, dict)
        self.assertIsInstance(response.data['id'], int)

    def test_notes_update_success(self):
        # get dummy note
        instance = self.create_note(self.note_1_payload)

        # request
        payload = self.note_2_payload
        request = self.factory.put(
            USER_NOTES_DETAIL_PATH,
            json.dumps(payload),
            content_type='application/json',
        )
        force_authenticate(request, user=self.user_1)
        response = self.get_view('update')(request, pk=instance.pk)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, dict)
        self.assertIsInstance(response.data['id'], int)
        self.assertEqual(response.data['id'], instance.pk)
        self.assertEqual(response.data['title'], payload['title'])
        self.assertEqual(response.data['body'], payload['body'])
        self.assertEqual(response.data['tags'], payload['tags'])

    def test_notes_delete_success(self):
        # get dummy note
        instance = self.create_note(self.note_1_payload)

        # request
        request = self.factory.delete(
            USER_NOTES_DETAIL_PATH,
        )
        force_authenticate(request, user=self.user_1)
        response = self.get_view('destroy')(request, pk=instance.pk)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, None)

    def test_notes_filter_tag_list(self):
        # get dummy note
        instance = self.create_note(self.note_1_payload)

        request = self.factory.get(PUBLIC_NOTES_TAG_FILTER_PATH)
        force_authenticate(request, user=self.user_1)
        response = self.get_view('filter')(request, key=instance.tags.first().title)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)

    def test_notes_owner_private_public(self):
        # get dummy note -  user 1
        note_1 = self.create_note(self.note_1_payload)

        request = self.factory.get(USER_NOTES_VIEW_PATH)
        force_authenticate(request, user=self.user_1)

        # Test owner can access while private=True
        response_1 = self.get_view('retrieve')(request, pk=note_1.pk)
        self.assertEqual(response_1.status_code, 200)
        self.assertIsInstance(response_1.data['id'], int)
        self.assertEqual(response_1.data['id'], note_1.pk)

        # Test owner can still access while private=False
        note_1.private = False
        note_1.save()

        response_2 = self.get_view('retrieve')(request, pk=note_1.pk)
        self.assertEqual(response_2.status_code, 200)
        self.assertIsInstance(response_2.data['id'], int)
        self.assertEqual(response_2.data['id'], note_1.pk)

    def test_notes_other_private_public(self):
        # get dummy note -  user 1
        note_1 = self.create_note(self.note_1_payload)

        request = self.factory.get(USER_NOTES_VIEW_PATH)
        # Switch force authentication to user_2
        force_authenticate(request, user=self.user_2)

        # Test user #2 can not access to other user note while private=True
        response_1 = self.get_view('retrieve')(request, pk=note_1.pk)
        self.assertEqual(response_1.status_code, 404)

        # Test user #2 can now access to other user note while private=False
        note_1.private = False
        note_1.save()

        response_2 = self.get_view('retrieve')(request, pk=note_1.pk)
        self.assertEqual(response_2.status_code, 200)
        self.assertIsInstance(response_2.data['id'], int)
        self.assertEqual(response_2.data['id'], note_1.pk)

    def test_notes_public_list(self):
        # get dummy note -  user 1
        note_1 = self.create_note(self.note_1_payload)

        request = self.factory.get(USER_NOTES_VIEW_PATH)
        # Switch force authentication to user_2
        force_authenticate(request, user=self.user_2)

        # Test user #2 can not access to other user note while private=True
        response_1 = self.get_view('public')(request)
        self.assertEqual(response_1.status_code, 200)
        self.assertIsInstance(response_1.data, list)
        self.assertEqual(len(response_1.data), 0)

        # Test user #2 can now access to other user note while private=False
        note_1.private = False
        note_1.save()

        response_2 = self.get_view('public')(request)
        self.assertEqual(response_2.status_code, 200)
        self.assertIsInstance(response_2.data, list)
        self.assertEqual(len(response_2.data), 1)




class TestUserCreate(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @classmethod
    def setUpClass(cls):
        cls.user_1 = _USER.objects.create_user(**{
            'username': 'dolph',
            'password': 'rut',
            'email': 'dolph@rut.com'
        })
        cls.user_2_payload = {
            'username': 'mario',
            'password': 'kart',
            'email': 'mario@kart.com'
        }

    @classmethod
    def tearDownClass(cls):
        cls.user_1.delete()

    def get_view(self, action):
        if action == 'create':
            return UserCreateView.as_view()

    def test_user_create_authentication(self):
        request = self.factory.post(USER_CREATE_VIEW_PATH)
        response = self.get_view('create')(request)
        self.assertEqual(response.status_code, 401)


    def test_user_create_validation(self):
        payload = {
        }
        request = self.factory.post(
            USER_CREATE_VIEW_PATH, json.dumps(payload),
            content_type='application/json'
        )
        force_authenticate(request, user=self.user_1)
        response = self.get_view('create')(request)

        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response.data, dict)
        self.assertEqual(response.data['username'][0].code, 'required')
        self.assertEqual(response.data['password'][0].code, 'required')
        self.assertEqual(response.data['email'][0].code, 'required')

    def test_user_create_success(self):
        payload = self.user_2_payload
        request = self.factory.post(
            USER_CREATE_VIEW_PATH, json.dumps(payload),
            content_type='application/json'
        )
        force_authenticate(request, user=self.user_1)
        response = self.get_view('create')(request)

        self.assertEqual(response.status_code, 201)
        self.assertIsInstance(response.data, dict)
        self.assertIsInstance(response.data['username'], str)
        self.assertIsInstance(response.data['email'], str)

        with self.assertRaises(KeyError, msg='password being exposed'):
            response.data['password']
