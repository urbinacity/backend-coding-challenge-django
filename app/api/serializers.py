from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.models import Note, Tag

_USER = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['title']

class NoteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    class Meta:
        model = Note
        fields = ['id', 'title', 'body', 'private', 'tags', 'created_by']
        extra_kwargs = {
            'created_by': {'required': False},
        }

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        tag_list = validated_data.pop('tags')
        tags = []

        for tag in tag_list:
            obj, created = Tag.objects.get_or_create(title=tag.get("title"))
            tags.append(obj)

        instance = super().create(validated_data)
        instance.tags.set(tags)
        return instance

    def update(self, instance, validated_data):
        tag_list = validated_data.pop('tags')
        tags = []

        for tag in tag_list:
            obj, created = Tag.objects.get_or_create(title=tag.get("title"))
            tags.append(obj)

        instance.tags.set(tags)
        instance.title = validated_data.get("title")
        instance.body = validated_data.get("body")
        instance.save()

        return instance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = _USER
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'username': {
                'min_length': 3,
                'trim_whitespace': True,
                'validators': [UniqueValidator(queryset=_USER.objects.all())]
            },
            'email': {
                'required': True,
                'allow_blank': False,
                'trim_whitespace': True,
            },
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        instance = _USER.objects.create_user(**validated_data)
        return instance