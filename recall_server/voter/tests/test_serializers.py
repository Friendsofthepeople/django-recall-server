import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.utils import timezone

from recall_server.voter.models import VoterProfile
from recall_server.voter.serializers import (
    VoterProfileSerializer, VoterProfileDetailSerializer, UserSerializer
)


class VoterSerializerTest(TestCase):
    """Test cases for the VoterProfile serializers."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.profile = self.user.voter_profile
        
        # Update profile with test data
        self.profile.constituency = 'Test Constituency'
        self.profile.ward = 'Test Ward'
        self.profile.county = 'Test County'
        self.profile.digital_signature = 'test_signature'
        self.profile.signature_public_key = 'test_public_key'
        self.profile.signature_date = timezone.now()
        self.profile.save()

    def test_user_serializer(self):
        """Test the UserSerializer."""
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data['username'], 'testuser')
        self.assertEqual(serializer.data['email'], 'test@example.com')
        self.assertEqual(serializer.data['first_name'], 'Test')
        self.assertEqual(serializer.data['last_name'], 'User')
        # Check that password field is not serialized
        self.assertNotIn('password', serializer.data)

    def test_voter_profile_serializer(self):
        """Test the VoterProfileSerializer."""
        serializer = VoterProfileSerializer(self.profile)
        self.assertEqual(serializer.data['user'], self.user.id)
        self.assertEqual(serializer.data['constituency'], 'Test Constituency')
        self.assertEqual(serializer.data['ward'], 'Test Ward')
        self.assertEqual(serializer.data['county'], 'Test County')
        self.assertEqual(serializer.data['digital_signature'], 'test_signature')
        self.assertEqual(serializer.data['signature_public_key'], 'test_public_key')
        self.assertIn('signature_date', serializer.data)
        self.assertFalse(serializer.data['signature_verified'])
        
    def test_voter_profile_detail_serializer(self):
        """Test the VoterProfileDetailSerializer."""
        serializer = VoterProfileDetailSerializer(self.profile)
        self.assertEqual(serializer.data['user_details']['username'], 'testuser')
        self.assertEqual(serializer.data['user_details']['email'], 'test@example.com')
        self.assertEqual(serializer.data['user_details']['first_name'], 'Test')
        self.assertEqual(serializer.data['user_details']['last_name'], 'User')
        
        # Check basic profile fields
        self.assertEqual(serializer.data['constituency'], 'Test Constituency')
        self.assertEqual(serializer.data['ward'], 'Test Ward')
        self.assertEqual(serializer.data['county'], 'Test County')
        
        # Check signature fields
        self.assertEqual(serializer.data['digital_signature'], 'test_signature')
        self.assertEqual(serializer.data['signature_public_key'], 'test_public_key')
        self.assertIn('signature_date', serializer.data)
        self.assertFalse(serializer.data['signature_verified'])
        
        # Check that representatives are included
        self.assertIn('representatives', serializer.data)
        self.assertIsInstance(serializer.data['representatives'], dict)
        self.assertIn('mp', serializer.data['representatives'])
        self.assertIn('senator', serializer.data['representatives'])
        self.assertIn('mca', serializer.data['representatives'])

    def test_serializer_create(self):
        """Test creating a profile through the serializer."""
        # Profile is created automatically with User
        user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='newpass123'
        )
        self.assertIsNotNone(hasattr(user, 'voter_profile'))
        
        # Test updating through serializer
        data = {
            'constituency': 'New Constituency',
            'ward': 'New Ward',
            'county': 'New County'
        }
        serializer = VoterProfileSerializer(user.voter_profile, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_profile = serializer.save()
        
        self.assertEqual(updated_profile.constituency, 'New Constituency')
        self.assertEqual(updated_profile.ward, 'New Ward')
        self.assertEqual(updated_profile.county, 'New County') 