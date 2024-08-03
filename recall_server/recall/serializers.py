"""
Model serializers for the `recall` Django app.
"""

from recall_server.recall.models import Recall
from rest_framework import serializers


class RecallSerializer(serializers.ModelSerializer):
    """
    Serializer to serialize/deserialize instances of the `Recall` model.
    """

    class Meta:
        model = Recall
        fields = [
            "created_at",
            "updated_at",
            "recalled",
            "recaller",
            "recall_supporters",
            "recall_reasons",
        ]
        read_only_fields = ["created_at", "updated_at"]
