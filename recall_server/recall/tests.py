from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
import datetime

from recall_server.recall.models import RecallPetition, PetitionSignature, RecallReason
from recall_server.county.models import County, SubCounty, Ward


class RecallPetitionModelTest(TestCase):
    """Test cases for the RecallPetition model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a county and ward
        self.county = County.objects.create(
            name="Test County",
            code="047",
            governor="Test Governor"
        )
        
        self.subcounty = SubCounty.objects.create(
            name="Test SubCounty",
            county=self.county,
            mp="Test MP"
        )
        
        self.ward = Ward.objects.create(
            name="Test Ward",
            subcounty=self.subcounty,
            mca="Test MCA"
        )
        
        # Create a recall petition
        self.petition = RecallPetition.objects.create(
            title="Test Recall Petition",
            target_name="Test MCA",
            target_position="MCA",
            ward=self.ward,
            initiator=self.user,
            signatures_required=1000,
            deadline=timezone.now() + datetime.timedelta(days=30),
            status="collecting"
        )
        
        # Create recall reasons
        self.reason1 = RecallReason.objects.create(
            petition=self.petition,
            reason="Reason 1",
            description="Description for reason 1"
        )
        
        self.reason2 = RecallReason.objects.create(
            petition=self.petition,
            reason="Reason 2",
            description="Description for reason 2"
        )
        
    def test_petition_creation(self):
        """Test creating a recall petition."""
        self.assertEqual(self.petition.title, "Test Recall Petition")
        self.assertEqual(self.petition.target_name, "Test MCA")
        self.assertEqual(self.petition.target_position, "MCA")
        self.assertEqual(self.petition.ward, self.ward)
        self.assertEqual(self.petition.initiator, self.user)
        self.assertEqual(self.petition.signatures_required, 1000)
        self.assertEqual(self.petition.signatures_count, 0)
        self.assertEqual(self.petition.status, "collecting")
        self.assertIsNotNone(self.petition.created_at)
        self.assertIsNotNone(self.petition.deadline)
        
    def test_string_representation(self):
        """Test string representation of a petition."""
        self.assertEqual(str(self.petition), "Test Recall Petition")
        
    def test_reason_relationship(self):
        """Test relationship with reasons."""
        reasons = self.petition.reasons.all()
        self.assertEqual(reasons.count(), 2)
        self.assertEqual(reasons[0].reason, "Reason 1")
        self.assertEqual(reasons[1].reason, "Reason 2")
        
    def test_is_active(self):
        """Test is_active property."""
        self.assertTrue(self.petition.is_active)
        
        # Change status to closed
        self.petition.status = "closed"
        self.petition.save()
        self.assertFalse(self.petition.is_active)
        
    def test_progress_percentage(self):
        """Test progress_percentage property."""
        self.assertEqual(self.petition.progress_percentage, 0)
        
        # Add some signatures
        self.petition.signatures_count = 500
        self.petition.save()
        self.assertEqual(self.petition.progress_percentage, 50)


class PetitionSignatureModelTest(TestCase):
    """Test cases for the PetitionSignature model."""
    
    def setUp(self):
        """Set up test data."""
        # Create users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password123'
        )
        
        # Create a county and ward
        self.county = County.objects.create(
            name="Test County",
            code="047",
            governor="Test Governor"
        )
        
        self.subcounty = SubCounty.objects.create(
            name="Test SubCounty",
            county=self.county,
            mp="Test MP"
        )
        
        self.ward = Ward.objects.create(
            name="Test Ward",
            subcounty=self.subcounty,
            mca="Test MCA"
        )
        
        # Create a recall petition
        self.petition = RecallPetition.objects.create(
            title="Test Recall Petition",
            target_name="Test MCA",
            target_position="MCA",
            ward=self.ward,
            initiator=self.user1,
            signatures_required=1000,
            deadline=timezone.now() + datetime.timedelta(days=30),
            status="collecting"
        )
        
        # Create a signature
        self.signature = PetitionSignature.objects.create(
            petition=self.petition,
            user=self.user2,
            id_number="12345678",
            phone_number="1234567890",
            verification_code="123456",
            is_verified=True
        )
        
    def test_signature_creation(self):
        """Test creating a petition signature."""
        self.assertEqual(self.signature.petition, self.petition)
        self.assertEqual(self.signature.user, self.user2)
        self.assertEqual(self.signature.id_number, "12345678")
        self.assertEqual(self.signature.phone_number, "1234567890")
        self.assertEqual(self.signature.verification_code, "123456")
        self.assertTrue(self.signature.is_verified)
        self.assertIsNotNone(self.signature.signed_at)
        
    def test_string_representation(self):
        """Test string representation of a signature."""
        expected = f"Signature by {self.user2.username} for {self.petition.title}"
        self.assertEqual(str(self.signature), expected)
        
    def test_unique_user_per_petition(self):
        """Test that a user can only sign a petition once."""
        # Try to create another signature for the same user and petition
        with self.assertRaises(Exception):  # Could be IntegrityError or ValidationError
            PetitionSignature.objects.create(
                petition=self.petition,
                user=self.user2,
                id_number="87654321",
                phone_number="0987654321",
                verification_code="654321",
                is_verified=True
            )


class RecallReasonModelTest(TestCase):
    """Test cases for the RecallReason model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a county and ward
        self.county = County.objects.create(
            name="Test County",
            code="047",
            governor="Test Governor"
        )
        
        self.subcounty = SubCounty.objects.create(
            name="Test SubCounty",
            county=self.county,
            mp="Test MP"
        )
        
        self.ward = Ward.objects.create(
            name="Test Ward",
            subcounty=self.subcounty,
            mca="Test MCA"
        )
        
        # Create a recall petition
        self.petition = RecallPetition.objects.create(
            title="Test Recall Petition",
            target_name="Test MCA",
            target_position="MCA",
            ward=self.ward,
            initiator=self.user,
            signatures_required=1000,
            deadline=timezone.now() + datetime.timedelta(days=30),
            status="collecting"
        )
        
        # Create a recall reason
        self.reason = RecallReason.objects.create(
            petition=self.petition,
            reason="Test Reason",
            description="Test Description"
        )
        
    def test_reason_creation(self):
        """Test creating a recall reason."""
        self.assertEqual(self.reason.petition, self.petition)
        self.assertEqual(self.reason.reason, "Test Reason")
        self.assertEqual(self.reason.description, "Test Description")
        
    def test_string_representation(self):
        """Test string representation of a reason."""
        self.assertEqual(str(self.reason), "Test Reason")
        
    def test_petition_relationship(self):
        """Test relationship with petition."""
        self.assertEqual(self.reason.petition, self.petition)


class RecallSerializerTest(TestCase):
    """Test cases for recall serializers."""
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='password123',
            is_staff=True
        )
        
        # Create a county and ward
        self.county = County.objects.create(
            name="Test County",
            code="047",
            governor="Test Governor"
        )
        
        self.subcounty = SubCounty.objects.create(
            name="Test SubCounty",
            county=self.county,
            mp="Test MP"
        )
        
        self.ward = Ward.objects.create(
            name="Test Ward",
            subcounty=self.subcounty,
            mca="Test MCA"
        )
        
        # Create a recall petition
        self.petition = RecallPetition.objects.create(
            title="Test Recall Petition",
            target_name="Test MCA",
            target_position="MCA",
            ward=self.ward,
            initiator=self.user,
            signatures_required=1000,
            deadline=timezone.now() + datetime.timedelta(days=30),
            status="collecting"
        )
        
        # Create recall reasons
        self.reason = RecallReason.objects.create(
            petition=self.petition,
            reason="Test Reason",
            description="Test Description"
        )
        
        # Create a signature
        self.signature = PetitionSignature.objects.create(
            petition=self.petition,
            user=self.admin_user,
            id_number="12345678",
            phone_number="1234567890",
            verification_code="123456",
            is_verified=True
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
    def test_petition_serialization(self):
        """Test petition serialization."""
        url = reverse('recallpetition-detail', kwargs={'pk': self.petition.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Recall Petition")
        self.assertEqual(response.data['target_name'], "Test MCA")
        self.assertEqual(response.data['target_position'], "MCA")
        self.assertEqual(response.data['ward'], self.ward.id)
        self.assertEqual(response.data['initiator'], self.user.id)
        self.assertEqual(response.data['signatures_required'], 1000)
        self.assertEqual(response.data['status'], "collecting")
        
    def test_reason_serialization(self):
        """Test reason serialization."""
        url = reverse('recallreason-detail', kwargs={'pk': self.reason.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['petition'], self.petition.id)
        self.assertEqual(response.data['reason'], "Test Reason")
        self.assertEqual(response.data['description'], "Test Description")
        
    def test_signature_serialization(self):
        """Test signature serialization."""
        url = reverse('petitionsignature-detail', kwargs={'pk': self.signature.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['petition'], self.petition.id)
        self.assertEqual(response.data['user'], self.admin_user.id)
        self.assertEqual(response.data['id_number'], "12345678")
        self.assertEqual(response.data['phone_number'], "1234567890")
        self.assertTrue(response.data['is_verified'])


class RecallPetitionViewTest(TestCase):
    """Test cases for the RecallPetition API views."""
    
    def setUp(self):
        """Set up test data."""
        # Create a client
        self.client = APIClient()
        
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password123'
        )
        
        # Create a county and ward
        self.county = County.objects.create(
            name="Test County",
            code="047",
            governor="Test Governor"
        )
        
        self.subcounty = SubCounty.objects.create(
            name="Test SubCounty",
            county=self.county,
            mp="Test MP"
        )
        
        self.ward = Ward.objects.create(
            name="Test Ward",
            subcounty=self.subcounty,
            mca="Test MCA"
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
        # Create a recall petition
        self.petition = RecallPetition.objects.create(
            title="Test Recall Petition",
            target_name="Test MCA",
            target_position="MCA",
            ward=self.ward,
            initiator=self.user,
            signatures_required=1000,
            deadline=timezone.now() + datetime.timedelta(days=30),
            status="collecting"
        )
        
    def test_list_petitions(self):
        """Test listing petitions."""
        url = reverse('recallpetition-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_petition(self):
        """Test retrieving a petition."""
        url = reverse('recallpetition-detail', kwargs={'pk': self.petition.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Recall Petition")
        
    def test_create_petition(self):
        """Test creating a petition."""
        url = reverse('recallpetition-list')
        data = {
            'title': 'New Recall Petition',
            'target_name': 'New Target',
            'target_position': 'Governor',
            'ward': self.ward.id,
            'initiator': self.user.id,
            'signatures_required': 5000,
            'deadline': (timezone.now() + datetime.timedelta(days=60)).isoformat(),
            'status': 'collecting'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RecallPetition.objects.count(), 2)
        self.assertEqual(RecallPetition.objects.get(title='New Recall Petition').target_name, 'New Target')
        
    def test_update_own_petition(self):
        """Test updating own petition."""
        url = reverse('recallpetition-detail', kwargs={'pk': self.petition.pk})
        data = {
            'title': 'Updated Petition Title'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.petition.refresh_from_db()
        self.assertEqual(self.petition.title, 'Updated Petition Title')
        
    def test_update_others_petition(self):
        """Test that users cannot update others' petitions."""
        # Change petition initiator
        self.petition.initiator = self.user2
        self.petition.save()
        
        url = reverse('recallpetition-detail', kwargs={'pk': self.petition.pk})
        data = {
            'title': 'Unauthorized Update'
        }
        response = self.client.patch(url, data)
        
        # Should be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.petition.refresh_from_db()
        self.assertEqual(self.petition.title, "Test Recall Petition")  # Unchanged
        
    def test_delete_own_petition(self):
        """Test deleting own petition."""
        url = reverse('recallpetition-detail', kwargs={'pk': self.petition.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RecallPetition.objects.count(), 0)
        
    def test_filter_petitions_by_ward(self):
        """Test filtering petitions by ward."""
        # Create another ward and petition
        ward2 = Ward.objects.create(
            name="Test Ward 2",
            subcounty=self.subcounty,
            mca="Test MCA 2"
        )
        
        RecallPetition.objects.create(
            title="Another Petition",
            target_name="Another MCA",
            target_position="MCA",
            ward=ward2,
            initiator=self.user,
            signatures_required=2000,
            deadline=timezone.now() + datetime.timedelta(days=45),
            status="collecting"
        )
        
        url = reverse('recallpetition-list') + f'?ward={self.ward.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Test Recall Petition")
        
    def test_filter_petitions_by_status(self):
        """Test filtering petitions by status."""
        # Create another petition with different status
        RecallPetition.objects.create(
            title="Closed Petition",
            target_name="Closed Target",
            target_position="MCA",
            ward=self.ward,
            initiator=self.user,
            signatures_required=1000,
            deadline=timezone.now() + datetime.timedelta(days=30),
            status="closed"
        )
        
        url = reverse('recallpetition-list') + '?status=closed'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Closed Petition")


class PetitionSignatureViewTest(TestCase):
    """Test cases for the PetitionSignature API views."""
    
    def setUp(self):
        """Set up test data."""
        # Create a client
        self.client = APIClient()
        
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password123'
        )
        
        # Create a county and ward
        self.county = County.objects.create(
            name="Test County",
            code="047",
            governor="Test Governor"
        )
        
        self.subcounty = SubCounty.objects.create(
            name="Test SubCounty",
            county=self.county,
            mp="Test MP"
        )
        
        self.ward = Ward.objects.create(
            name="Test Ward",
            subcounty=self.subcounty,
            mca="Test MCA"
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
        # Create a recall petition
        self.petition = RecallPetition.objects.create(
            title="Test Recall Petition",
            target_name="Test MCA",
            target_position="MCA",
            ward=self.ward,
            initiator=self.user,
            signatures_required=1000,
            deadline=timezone.now() + datetime.timedelta(days=30),
            status="collecting"
        )
        
        # Create a signature
        self.signature = PetitionSignature.objects.create(
            petition=self.petition,
            user=self.user2,
            id_number="12345678",
            phone_number="1234567890",
            verification_code="123456",
            is_verified=True
        )
        
    def test_list_signatures(self):
        """Test listing signatures."""
        url = reverse('petitionsignature-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_signature(self):
        """Test retrieving a signature."""
        url = reverse('petitionsignature-detail', kwargs={'pk': self.signature.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['petition'], self.petition.id)
        self.assertEqual(response.data['user'], self.user2.id)
        
    def test_create_signature(self):
        """Test creating a signature."""
        url = reverse('petitionsignature-list')
        data = {
            'petition': self.petition.id,
            'user': self.user.id,
            'id_number': '87654321',
            'phone_number': '0987654321',
            'verification_code': '654321',
            'is_verified': False
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PetitionSignature.objects.count(), 2)
        self.assertEqual(PetitionSignature.objects.get(id_number='87654321').phone_number, '0987654321')
        
    def test_verify_signature(self):
        """Test verifying a signature."""
        # Create an unverified signature
        signature = PetitionSignature.objects.create(
            petition=self.petition,
            user=self.user,
            id_number="11111111",
            phone_number="1111111111",
            verification_code="111111",
            is_verified=False
        )
        
        url = reverse('petitionsignature-detail', kwargs={'pk': signature.pk})
        data = {
            'is_verified': True
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        signature.refresh_from_db()
        self.assertTrue(signature.is_verified)
        
    def test_filter_signatures_by_petition(self):
        """Test filtering signatures by petition."""
        # Create another petition and signature
        petition2 = RecallPetition.objects.create(
            title="Another Petition",
            target_name="Another Target",
            target_position="Governor",
            ward=self.ward,
            initiator=self.user,
            signatures_required=5000,
            deadline=timezone.now() + datetime.timedelta(days=60),
            status="collecting"
        )
        
        PetitionSignature.objects.create(
            petition=petition2,
            user=self.user,
            id_number="99999999",
            phone_number="9999999999",
            verification_code="999999",
            is_verified=True
        )
        
        url = reverse('petitionsignature-list') + f'?petition={self.petition.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id_number'], "12345678")
        
    def test_filter_signatures_by_verified(self):
        """Test filtering signatures by verification status."""
        # Create an unverified signature
        PetitionSignature.objects.create(
            petition=self.petition,
            user=self.user,
            id_number="22222222",
            phone_number="2222222222",
            verification_code="222222",
            is_verified=False
        )
        
        url = reverse('petitionsignature-list') + '?is_verified=true'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id_number'], "12345678")


class RecallReasonViewTest(TestCase):
    """Test cases for the RecallReason API views."""
    
    def setUp(self):
        """Set up test data."""
        # Create a client
        self.client = APIClient()
        
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a county and ward
        self.county = County.objects.create(
            name="Test County",
            code="047",
            governor="Test Governor"
        )
        
        self.subcounty = SubCounty.objects.create(
            name="Test SubCounty",
            county=self.county,
            mp="Test MP"
        )
        
        self.ward = Ward.objects.create(
            name="Test Ward",
            subcounty=self.subcounty,
            mca="Test MCA"
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
        # Create a recall petition
        self.petition = RecallPetition.objects.create(
            title="Test Recall Petition",
            target_name="Test MCA",
            target_position="MCA",
            ward=self.ward,
            initiator=self.user,
            signatures_required=1000,
            deadline=timezone.now() + datetime.timedelta(days=30),
            status="collecting"
        )
        
        # Create recall reasons
        self.reason = RecallReason.objects.create(
            petition=self.petition,
            reason="Test Reason",
            description="Test Description"
        )
        
    def test_list_reasons(self):
        """Test listing reasons."""
        url = reverse('recallreason-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_reason(self):
        """Test retrieving a reason."""
        url = reverse('recallreason-detail', kwargs={'pk': self.reason.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['petition'], self.petition.id)
        self.assertEqual(response.data['reason'], "Test Reason")
        self.assertEqual(response.data['description'], "Test Description")
        
    def test_create_reason(self):
        """Test creating a reason."""
        url = reverse('recallreason-list')
        data = {
            'petition': self.petition.id,
            'reason': 'New Reason',
            'description': 'New Description'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RecallReason.objects.count(), 2)
        self.assertEqual(RecallReason.objects.get(reason='New Reason').description, 'New Description')
        
    def test_update_reason(self):
        """Test updating a reason."""
        url = reverse('recallreason-detail', kwargs={'pk': self.reason.pk})
        data = {
            'description': 'Updated Description'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reason.refresh_from_db()
        self.assertEqual(self.reason.description, 'Updated Description')
        
    def test_delete_reason(self):
        """Test deleting a reason."""
        url = reverse('recallreason-detail', kwargs={'pk': self.reason.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RecallReason.objects.count(), 0)
        
    def test_filter_reasons_by_petition(self):
        """Test filtering reasons by petition."""
        # Create another petition and reason
        petition2 = RecallPetition.objects.create(
            title="Another Petition",
            target_name="Another Target",
            target_position="Governor",
            ward=self.ward,
            initiator=self.user,
            signatures_required=5000,
            deadline=timezone.now() + datetime.timedelta(days=60),
            status="collecting"
        )
        
        RecallReason.objects.create(
            petition=petition2,
            reason="Another Reason",
            description="Another Description"
        )
        
        url = reverse('recallreason-list') + f'?petition={self.petition.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['reason'], "Test Reason") 