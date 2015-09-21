from rest_framework import serializers
from core import models

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.User
        fields = ['username']
