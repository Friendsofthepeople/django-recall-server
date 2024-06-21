from rest_framework import serializers
from .models import Recall

class RecallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recall
        fields = ['id', 'created_at', 'updated_at', 'recalled', 'recaller', 'recall_supporters', 'recall_reasons']
        read_only_fields = ['created_at', 'updated_at']