"""
Model serializers for the `voter` Django app.
"""

from django.contrib.auth.hashers import make_password
from recall_server.voter.models import  VoterProfile
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class VoterSerializer(serializers.ModelSerializer):
    """
    Serializer for the Django User model.
    """
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "date_joined",
            "last_login",
            "is_active",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


class VoterProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the VoterProfile model.
    """
    user = VoterSerializer()
    
    class Meta:
        model = VoterProfile
        fields = [
            "user",
            "tokenized_id",
            # "profile_picture",
            "bio",
            "county",
            "constituency",
            "ward",
            "created_at",
            "updated_at",
            "notify_on_new_bills",
            "notify_on_bill_status_change",
            "notify_on_vote",
            "interests",
            "digital_signature",
            "signature_public_key",
            "signature_verified",
            "signature_date",
        ]
        read_only_fields = ["tokenized_id", "created_at", "updated_at", "signature_verified"]
        
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(
            username=user_data['username'],
            email=user_data['email'],
            password=make_password(user_data['password']),
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )
        
        profile = user.voter_profile
        for attr, value in validated_data.items():
            setattr(profile, attr, value)
        profile.save()
        
        return profile
        
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                if attr == 'password':
                    user.set_password(value)
                else:
                    setattr(user, attr, value)
            user.save()
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class VoterProfileDetailSerializer(VoterProfileSerializer):
    """
    Detailed serializer for VoterProfile with additional information.
    """
    representatives = serializers.SerializerMethodField()
    voting_history_count = serializers.SerializerMethodField()
    followed_bills_count = serializers.SerializerMethodField()
    representative_alignment = serializers.SerializerMethodField()
    
    class Meta(VoterProfileSerializer.Meta):
        fields = VoterProfileSerializer.Meta.fields + [
            "followed_bills",
            "followed_mps",
            "followed_senators",
            "followed_mcas",
            "representatives",
            "voting_history_count",
            "followed_bills_count",
            "representative_alignment",
        ]
        
    def get_representatives(self, obj):
        reps = obj.get_representatives()
        result = {}
        
        for rep_type, rep in reps.items():
            if rep:
                result[rep_type] = {
                    'id': rep.id if hasattr(rep, 'id') else rep.tokenized_id,
                    'name': rep.name
                }
            else:
                result[rep_type] = None
                
        return result
        
    def get_voting_history_count(self, obj):
        return obj.get_voting_history().count()
        
    def get_followed_bills_count(self, obj):
        return obj.followed_bills.count()
        
    def get_representative_alignment(self, obj):
        return obj.get_representative_alignment()


# Legacy serializer for backward compatibility
# class VoterSerializer(serializers.ModelSerializer):
#     """
#     Legacy serializer for the Voter model.
#     This is kept for backward compatibility and will be deprecated.
#     """
#     class Meta:
#         model = Voter
#         fields = [
#             "first_name",
#             "last_name",
#             "email",
#             "username",
#             "password",
#             "tokenized_id",
#             "created_at",
#             "profile_picture",
#             "bio",
#             "county",
#             "constituency",
#             "ward",
#             "is_verified",
#             "date_joined",
#         ]
#         read_only_fields = ["tokenized_id", "created_at", "date_joined"]
#         extra_kwargs = {"password": {"write_only": True}}

#     def create(self, validated_data):
#         validated_data["password"] = make_password(validated_data["password"])
#         return super().create(validated_data)
