from rest_framework.serializers import ModelSerializer
from ChatBotAi.models import Message

class MessageSeralizer(ModelSerializer):
    class Meta:
        model = Message
        fields = ['text' , 'created_at' , 'role']
        read_only_fields = ['text' , 'created_at', 'role']