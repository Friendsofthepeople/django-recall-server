import base64
import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from recall_server.voter.models import VoterProfile
try:
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


class VoterProfileModelTest(TestCase):
    """Test cases for the VoterProfile model."""

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

    def test_voter_profile_creation(self):
        """Test that a VoterProfile is created automatically when a User is created."""
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.user, self.user)
        self.assertTrue(self.profile.is_active)

    def test_get_full_name(self):
        """Test get_full_name method returns the User's full name."""
        self.assertEqual(self.profile.get_full_name(), 'Test User')

    @unittest.skipIf(not CRYPTOGRAPHY_AVAILABLE, "Cryptography package not available")
    def test_generate_keypair(self):
        """Test generating a keypair."""
        private_key, public_key = self.profile.generate_keypair()
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        self.assertTrue(private_key.startswith('-----BEGIN PRIVATE KEY-----'))
        self.assertTrue(public_key.startswith('-----BEGIN PUBLIC KEY-----'))
        self.assertEqual(self.profile.signature_public_key, public_key)

    @unittest.skipIf(not CRYPTOGRAPHY_AVAILABLE, "Cryptography package not available")
    def test_sign_message(self):
        """Test signing a message."""
        # Generate keypair
        private_key, _ = self.profile.generate_keypair()
        
        # Sign a message
        message = "This is a test message"
        signature = self.profile.sign_message(message, private_key)
        
        # Verify signature was created and stored
        self.assertIsNotNone(signature)
        self.assertEqual(self.profile.digital_signature, signature)
        self.assertIsNotNone(self.profile.signature_date)

    @unittest.skipIf(not CRYPTOGRAPHY_AVAILABLE, "Cryptography package not available")
    def test_verify_signature(self):
        """Test verifying a signature."""
        # Generate keypair
        private_key, _ = self.profile.generate_keypair()
        
        # Sign a message
        message = "This is a test message"
        self.profile.sign_message(message, private_key)
        
        # Verify the signature
        is_valid = self.profile.verify_signature(message)
        self.assertTrue(is_valid)
        self.assertTrue(self.profile.signature_verified)

    @unittest.skipIf(not CRYPTOGRAPHY_AVAILABLE, "Cryptography package not available")
    def test_verify_invalid_signature(self):
        """Test verifying an invalid signature."""
        # Generate keypair
        private_key, _ = self.profile.generate_keypair()
        
        # Sign a message
        message = "This is a test message"
        self.profile.sign_message(message, private_key)
        
        # Try to verify with a different message
        is_valid = self.profile.verify_signature("This is a different message")
        self.assertFalse(is_valid)
        self.assertFalse(self.profile.signature_verified)

    def test_update_signature(self):
        """Test updating a signature."""
        # Create test data
        signature = "test_signature"
        public_key = "test_public_key"
        
        # Update signature
        self.profile.update_signature(signature, public_key)
        
        # Verify signature was updated
        self.assertEqual(self.profile.digital_signature, signature)
        self.assertEqual(self.profile.signature_public_key, public_key)
        self.assertIsNotNone(self.profile.signature_date)
        self.assertFalse(self.profile.signature_verified)

    def test_get_representatives(self):
        """Test getting representatives."""
        # This is a simple test that just verifies the method returns a dict with the correct keys
        # In a real test, you would mock the required models and test with actual data
        reps = self.profile.get_representatives()
        self.assertIsInstance(reps, dict)
        self.assertIn('mp', reps)
        self.assertIn('senator', reps)
        self.assertIn('mca', reps) 