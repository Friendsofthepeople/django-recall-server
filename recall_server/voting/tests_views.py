from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from recall_server.voting.models import PublicVote, OfficialVote, VoteChoices
from recall_server.laws.models import Bill


class MockLegislator:
    """Mock class for legislator testing."""
    
    def __init__(self, name, id):
        self.name = name
        self.id = id


class MockCounty:
    """Mock class for county testing."""
    
    def __init__(self, id, name):
        self.id = id
        self.name = name
        
    def save(self, *args, **kwargs):
        pass


class PublicVoteViewTest(TestCase):
    """Test cases for the PublicVote API views."""

    def setUp(self):
        """Set up test data."""
        # Create a client
        self.client = APIClient()
        
        # Create users for testing
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
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)

        # Create a bill
        self.bill = Bill.objects.create(
            bill_number='TEST-001',
            title='Test Bill',
            description='A test bill',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='public_participation',  # Make it available for voting
            bill_type='private'
        )
        
        # Mock a region/county
        self.region = MockCounty(1, "Test County")
        
        # Monkey patch the bill to allow voting
        def can_be_voted():
            return True
        self.bill.can_be_voted = can_be_voted
        
        # Create a vote
        self.vote = PublicVote.objects.create(
            bill=self.bill,
            user=self.user,
            vote=VoteChoices.YES,
            comment="Test comment",
            region=self.region
        )
        
    def test_list_public_votes(self):
        """Test listing public votes."""
        url = reverse('publicvote-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_public_vote(self):
        """Test retrieving a public vote."""
        url = reverse('publicvote-detail', kwargs={'pk': self.vote.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bill'], self.bill.id)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['vote'], VoteChoices.YES)
        self.assertEqual(response.data['comment'], "Test comment")
        
    def test_create_public_vote(self):
        """Test creating a public vote."""
        # Create another bill
        bill2 = Bill.objects.create(
            bill_number='TEST-002',
            title='Test Bill 2',
            description='Another test bill',
            sponsor='Test Sponsor 2',
            proposer=self.admin_user,
            status='public_participation',  # Make it available for voting
            bill_type='private'
        )
        
        # Monkey patch the second bill to allow voting
        bill2.can_be_voted = can_be_voted
        
        url = reverse('publicvote-list')
        data = {
            'bill': bill2.id,
            'user': self.user.id,
            'vote': VoteChoices.NO,
            'comment': "New comment",
            'region': self.region.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['bill'], bill2.id)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['vote'], VoteChoices.NO)
        self.assertEqual(response.data['comment'], "New comment")
        
    def test_update_public_vote(self):
        """Test updating a public vote."""
        url = reverse('publicvote-detail', kwargs={'pk': self.vote.pk})
        data = {
            'comment': 'Updated comment',
            'vote': VoteChoices.ABSTAIN
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], 'Updated comment')
        self.assertEqual(response.data['vote'], VoteChoices.ABSTAIN)
        
    def test_delete_public_vote(self):
        """Test deleting a public vote."""
        url = reverse('publicvote-detail', kwargs={'pk': self.vote.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PublicVote.objects.count(), 0)
        
    def test_filter_public_votes_by_bill(self):
        """Test filtering public votes by bill."""
        url = reverse('publicvote-list') + f'?bill={self.bill.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test filtering by non-existent bill
        url = reverse('publicvote-list') + '?bill=999'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
    def test_filter_public_votes_by_user(self):
        """Test filtering public votes by user."""
        url = reverse('publicvote-list') + f'?user={self.user.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test filtering by non-existent user
        url = reverse('publicvote-list') + '?user=999'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
    def test_filter_public_votes_by_vote(self):
        """Test filtering public votes by vote."""
        url = reverse('publicvote-list') + f'?vote={VoteChoices.YES}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test filtering by different vote
        url = reverse('publicvote-list') + f'?vote={VoteChoices.NO}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
    def test_unauthorized_access(self):
        """Test unauthorized access to public vote endpoints."""
        # Logout
        self.client.force_authenticate(user=None)
        
        # Try to list public votes
        url = reverse('publicvote-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Try to create a public vote
        data = {
            'bill': self.bill.id,
            'user': self.user.id,
            'vote': VoteChoices.NO,
            'comment': "Unauthorized comment",
            'region': self.region.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OfficialVoteViewTest(TestCase):
    """Test cases for the OfficialVote API views."""

    def setUp(self):
        """Set up test data."""
        # Create a client
        self.client = APIClient()
        
        # Create users for testing
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
        
        # Authenticate the client as admin (since managing official votes is admin-only)
        self.client.force_authenticate(user=self.admin_user)

        # Create a bill
        self.bill = Bill.objects.create(
            bill_number='TEST-001',
            title='Test Bill',
            description='A test bill',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='committee',  # Bill in committee stage
            bill_type='private'
        )
        
        # Create a mock legislator
        self.legislator = MockLegislator(name="Test Legislator", id=1)
        self.content_type = ContentType.objects.get_for_model(User)  # Using User as mock model
        
        # Monkey patch bill update_vote_counts method
        def update_vote_counts():
            pass
        self.bill.update_vote_counts = update_vote_counts
        
        # Create a vote
        self.vote = OfficialVote.objects.create(
            bill=self.bill,
            legislator_content_type=self.content_type,
            legislator_object_id=self.admin_user.id,
            vote=VoteChoices.YES,
            session_name="Test Session",
            reason="Test reason"
        )
        
    def test_list_official_votes(self):
        """Test listing official votes."""
        url = reverse('officialvote-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_official_vote(self):
        """Test retrieving an official vote."""
        url = reverse('officialvote-detail', kwargs={'pk': self.vote.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bill'], self.bill.id)
        self.assertEqual(response.data['legislator_content_type'], self.content_type.id)
        self.assertEqual(response.data['legislator_object_id'], self.admin_user.id)
        self.assertEqual(response.data['vote'], VoteChoices.YES)
        self.assertEqual(response.data['session_name'], "Test Session")
        self.assertEqual(response.data['reason'], "Test reason")
        
    def test_create_official_vote(self):
        """Test creating an official vote."""
        url = reverse('officialvote-list')
        data = {
            'bill': self.bill.id,
            'legislator_content_type': self.content_type.id,
            'legislator_object_id': self.user.id,
            'vote': VoteChoices.NO,
            'session_name': "New Session",
            'reason': "New reason"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['bill'], self.bill.id)
        self.assertEqual(response.data['legislator_content_type'], self.content_type.id)
        self.assertEqual(response.data['legislator_object_id'], self.user.id)
        self.assertEqual(response.data['vote'], VoteChoices.NO)
        self.assertEqual(response.data['session_name'], "New Session")
        self.assertEqual(response.data['reason'], "New reason")
        
    def test_update_official_vote(self):
        """Test updating an official vote."""
        url = reverse('officialvote-detail', kwargs={'pk': self.vote.pk})
        data = {
            'reason': 'Updated reason',
            'vote': VoteChoices.ABSTAIN
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reason'], 'Updated reason')
        self.assertEqual(response.data['vote'], VoteChoices.ABSTAIN)
        
    def test_delete_official_vote(self):
        """Test deleting an official vote."""
        url = reverse('officialvote-detail', kwargs={'pk': self.vote.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(OfficialVote.objects.count(), 0)
        
    def test_filter_official_votes_by_bill(self):
        """Test filtering official votes by bill."""
        url = reverse('officialvote-list') + f'?bill={self.bill.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test filtering by non-existent bill
        url = reverse('officialvote-list') + '?bill=999'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
    def test_filter_official_votes_by_legislator(self):
        """Test filtering official votes by legislator."""
        url = reverse('officialvote-list') + f'?legislator_object_id={self.admin_user.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test filtering by non-existent legislator
        url = reverse('officialvote-list') + '?legislator_object_id=999'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
    def test_filter_official_votes_by_vote(self):
        """Test filtering official votes by vote."""
        url = reverse('officialvote-list') + f'?vote={VoteChoices.YES}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test filtering by different vote
        url = reverse('officialvote-list') + f'?vote={VoteChoices.NO}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
    def test_non_admin_access(self):
        """Test non-admin access to official vote endpoints."""
        # Authenticate as a regular user
        self.client.force_authenticate(user=self.user)
        
        # Try to create an official vote
        url = reverse('officialvote-list')
        data = {
            'bill': self.bill.id,
            'legislator_content_type': self.content_type.id,
            'legislator_object_id': self.user.id,
            'vote': VoteChoices.NO,
            'session_name': "Unauthorized Session",
            'reason': "Unauthorized reason"
        }
        response = self.client.post(url, data)
        # Should be forbidden since the user is not an admin
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 