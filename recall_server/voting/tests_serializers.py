from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from recall_server.voting.models import PublicVote, OfficialVote, VoteChoices
from recall_server.voting.serializers import PublicVoteSerializer, OfficialVoteSerializer
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


class PublicVoteSerializerTest(TestCase):
    """Test cases for the PublicVoteSerializer."""

    def setUp(self):
        """Set up test data."""
        # Create a user for testing
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

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
        
    def test_public_vote_serializer(self):
        """Test serializing a public vote."""
        serializer = PublicVoteSerializer(self.vote)
        
        # Verify serialized data
        self.assertEqual(serializer.data['bill'], self.bill.id)
        self.assertEqual(serializer.data['user'], self.user.id)
        self.assertEqual(serializer.data['vote'], VoteChoices.YES)
        self.assertEqual(serializer.data['comment'], "Test comment")
        self.assertEqual(serializer.data['region'], self.region.id)
        self.assertIn('date', serializer.data)
        
    def test_public_vote_serializer_create(self):
        """Test creating a public vote using the serializer."""
        # Create a new user
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='password123'
        )
        
        # Create serializer data
        data = {
            'bill': self.bill.id,
            'user': new_user.id,
            'vote': VoteChoices.NO,
            'comment': 'New comment',
            'region': self.region.id
        }
        
        # Create serializer
        serializer = PublicVoteSerializer(data=data)
        
        # Validate serializer
        self.assertTrue(serializer.is_valid())
        
        # Save serializer
        vote = serializer.save()
        
        # Verify vote
        self.assertEqual(vote.bill, self.bill)
        self.assertEqual(vote.user, new_user)
        self.assertEqual(vote.vote, VoteChoices.NO)
        self.assertEqual(vote.comment, 'New comment')
        self.assertEqual(vote.region, self.region)
        
    def test_public_vote_serializer_update(self):
        """Test updating a public vote using the serializer."""
        # Create update data
        data = {
            'comment': 'Updated comment',
            'vote': VoteChoices.ABSTAIN
        }
        
        # Create serializer
        serializer = PublicVoteSerializer(self.vote, data=data, partial=True)
        
        # Validate serializer
        self.assertTrue(serializer.is_valid())
        
        # Save serializer
        vote = serializer.save()
        
        # Verify vote
        self.assertEqual(vote.comment, 'Updated comment')
        self.assertEqual(vote.vote, VoteChoices.ABSTAIN)
        
    def test_public_vote_serializer_validation(self):
        """Test validating a public vote using the serializer."""
        # Create invalid data (missing required fields)
        data = {
            'comment': 'Invalid vote'
        }
        
        # Create serializer
        serializer = PublicVoteSerializer(data=data)
        
        # Validate serializer
        self.assertFalse(serializer.is_valid())
        self.assertIn('bill', serializer.errors)
        self.assertIn('user', serializer.errors)
        self.assertIn('vote', serializer.errors)
        self.assertIn('region', serializer.errors)


class OfficialVoteSerializerTest(TestCase):
    """Test cases for the OfficialVoteSerializer."""

    def setUp(self):
        """Set up test data."""
        # Create a user for testing
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

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
            legislator_object_id=self.user.id,
            vote=VoteChoices.YES,
            session_name="Test Session",
            reason="Test reason"
        )
        
    def test_official_vote_serializer(self):
        """Test serializing an official vote."""
        serializer = OfficialVoteSerializer(self.vote)
        
        # Verify serialized data
        self.assertEqual(serializer.data['bill'], self.bill.id)
        self.assertEqual(serializer.data['legislator_content_type'], self.content_type.id)
        self.assertEqual(serializer.data['legislator_object_id'], self.user.id)
        self.assertEqual(serializer.data['vote'], VoteChoices.YES)
        self.assertEqual(serializer.data['session_name'], "Test Session")
        self.assertEqual(serializer.data['reason'], "Test reason")
        self.assertIn('date', serializer.data)
        
    def test_official_vote_serializer_create(self):
        """Test creating an official vote using the serializer."""
        # Create serializer data
        data = {
            'bill': self.bill.id,
            'legislator_content_type': self.content_type.id,
            'legislator_object_id': self.legislator.id,
            'vote': VoteChoices.NO,
            'session_name': 'New Session',
            'reason': 'New reason'
        }
        
        # Create serializer
        serializer = OfficialVoteSerializer(data=data)
        
        # Validate serializer
        self.assertTrue(serializer.is_valid())
        
        # Save serializer
        vote = serializer.save()
        
        # Verify vote
        self.assertEqual(vote.bill, self.bill)
        self.assertEqual(vote.legislator_content_type, self.content_type)
        self.assertEqual(vote.legislator_object_id, self.legislator.id)
        self.assertEqual(vote.vote, VoteChoices.NO)
        self.assertEqual(vote.session_name, 'New Session')
        self.assertEqual(vote.reason, 'New reason')
        
    def test_official_vote_serializer_update(self):
        """Test updating an official vote using the serializer."""
        # Create update data
        data = {
            'reason': 'Updated reason',
            'vote': VoteChoices.ABSTAIN
        }
        
        # Create serializer
        serializer = OfficialVoteSerializer(self.vote, data=data, partial=True)
        
        # Validate serializer
        self.assertTrue(serializer.is_valid())
        
        # Save serializer
        vote = serializer.save()
        
        # Verify vote
        self.assertEqual(vote.reason, 'Updated reason')
        self.assertEqual(vote.vote, VoteChoices.ABSTAIN)
        
    def test_official_vote_serializer_validation(self):
        """Test validating an official vote using the serializer."""
        # Create invalid data (missing required fields)
        data = {
            'reason': 'Invalid vote'
        }
        
        # Create serializer
        serializer = OfficialVoteSerializer(data=data)
        
        # Validate serializer
        self.assertFalse(serializer.is_valid())
        self.assertIn('bill', serializer.errors)
        self.assertIn('legislator_content_type', serializer.errors)
        self.assertIn('legislator_object_id', serializer.errors)
        self.assertIn('vote', serializer.errors) 