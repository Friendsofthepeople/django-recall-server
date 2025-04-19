import json
import base64
import unittest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from recall_server.voter.models import VoterProfile
try:
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


class VoterProfileViewsetTest(TestCase):
    """Test cases for the VoterProfile API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.profile = self.user.voter_profile
        # Authenticate
        self.client.force_authenticate(user=self.user)
        # Create additional users for testing
        self.other_user = User.objects.create_user(username='otheruser', password='password123')

    def test_get_profile(self):
        """Test retrieving a user's profile."""
        url = reverse('voter_profile-detail', kwargs={'pk': self.profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)

    def test_list_profiles(self):
        """Test listing profiles."""
        url = reverse('voter_profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Our user and the other_user

    def test_update_profile(self):
        """Test updating a profile."""
        url = reverse('voter_profile-detail', kwargs={'pk': self.profile.pk})
        data = {
            'constituency': 'Test Constituency',
            'ward': 'Test Ward',
            'county': 'Test County'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Refresh from db
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.constituency, 'Test Constituency')
        self.assertEqual(self.profile.ward, 'Test Ward')
        self.assertEqual(self.profile.county, 'Test County')

    def test_update_other_profile_forbidden(self):
        """Test that updating another user's profile is forbidden."""
        url = reverse('voter_profile-detail', kwargs={'pk': self.other_user.voter_profile.pk})
        data = {'constituency': 'Test Constituency'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @unittest.skipIf(not CRYPTOGRAPHY_AVAILABLE, "Cryptography package not available")
    def test_generate_keypair(self):
        """Test generating a keypair through the API."""
        url = reverse('voter_profile-generate-keypair')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify response has keys
        self.assertIn('private_key', response.data)
        self.assertIn('public_key', response.data)
        # Refresh from db and check public key was stored
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.signature_public_key, response.data['public_key'])

    @unittest.skipIf(not CRYPTOGRAPHY_AVAILABLE, "Cryptography package not available")
    def test_sign_message(self):
        """Test signing a message through the API."""
        # First generate a keypair
        keypair_url = reverse('voter_profile-generate-keypair')
        keypair_response = self.client.post(keypair_url)
        private_key = keypair_response.data['private_key']
        
        # Now sign a message
        url = reverse('voter_profile-sign-message')
        data = {
            'message': 'This is a test message',
            'private_key': private_key
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('signature', response.data)
        
        # Refresh from db and check signature was stored
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.digital_signature, response.data['signature'])
        self.assertIsNotNone(self.profile.signature_date)

    @unittest.skipIf(not CRYPTOGRAPHY_AVAILABLE, "Cryptography package not available")
    def test_verify_signature(self):
        """Test verifying a signature through the API."""
        # First generate a keypair
        keypair_url = reverse('voter_profile-generate-keypair')
        keypair_response = self.client.post(keypair_url)
        private_key = keypair_response.data['private_key']
        
        # Sign a message
        sign_url = reverse('voter_profile-sign-message')
        message = 'This is a test message'
        sign_data = {
            'message': message,
            'private_key': private_key
        }
        self.client.post(sign_url, sign_data)
        
        # Now verify the signature
        verify_url = reverse('voter_profile-verify-signature')
        verify_data = {
            'message': message
        }
        response = self.client.post(verify_url, verify_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_valid'])
        
        # Refresh from db and check verified flag was set
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.signature_verified)

    @unittest.skipIf(not CRYPTOGRAPHY_AVAILABLE, "Cryptography package not available")
    def test_verify_invalid_signature(self):
        """Test verifying an invalid signature through the API."""
        # First generate a keypair
        keypair_url = reverse('voter_profile-generate-keypair')
        keypair_response = self.client.post(keypair_url)
        private_key = keypair_response.data['private_key']
        
        # Sign a message
        sign_url = reverse('voter_profile-sign-message')
        message = 'This is a test message'
        sign_data = {
            'message': message,
            'private_key': private_key
        }
        self.client.post(sign_url, sign_data)
        
        # Now verify with a different message
        verify_url = reverse('voter_profile-verify-signature')
        verify_data = {
            'message': 'This is a different message'
        }
        response = self.client.post(verify_url, verify_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_valid'])
        
        # Refresh from db and check verified flag was not set
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.signature_verified)

    def test_get_representatives(self):
        """Test retrieving a user's representatives."""
        url = reverse('voter_profile-representatives')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check response structure
        self.assertIn('mp', response.data)
        self.assertIn('senator', response.data)
        self.assertIn('mca', response.data) 