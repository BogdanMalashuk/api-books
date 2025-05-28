from rest_framework import serializers
from .models import Book, Genre, User
from mongoengine.errors import DoesNotExist


class UserSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class BookSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField()
    author = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False)
    genre = serializers.CharField()
    is_borrowed = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        try:
            genre = Genre.objects.get(id=validated_data.pop("genre"))
        except DoesNotExist:
            raise serializers.ValidationError({"genre": "Genre not found."})
        return Book.objects.create(genre=genre, **validated_data)

    def update(self, instance, validated_data):
        if "genre" in validated_data:
            try:
                genre = Genre.objects.get(id=validated_data.pop("genre"))
                instance.genre = genre
            except DoesNotExist:
                raise serializers.ValidationError({"genre": "Genre not found."})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class BorrowRecordSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    book = BookSerializer()
    borrowed_at = serializers.DateTimeField()
    returned_at = serializers.DateTimeField(allow_null=True)


class GenreSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()

    def create(self, validated_data):
        genre = Genre(**validated_data)
        genre.save()
        return genre

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.save()
        return instance
