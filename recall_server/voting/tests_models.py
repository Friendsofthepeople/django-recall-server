from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.core.exceptions import ValidationError

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


class PublicVoteModelTest(TestCase):
    """Test cases for the PublicVote model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create another user for duplicate vote tests
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
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
        
        # Mock region
        self.region = MockCounty(1, "Test County")
        
    def test_create_public_vote(self):
        """Test creating a public vote."""
        vote = PublicVote.objects.create(
            bill=self.bill,
            user=self.user,
            vote=VoteChoices.YES,
            comment="Test comment",
            region=self.region
        )
        
        self.assertEqual(vote.bill, self.bill)
        self.assertEqual(vote.user, self.user)
        self.assertEqual(vote.vote, VoteChoices.YES)
        self.assertEqual(vote.comment, "Test comment")
        self.assertEqual(vote.region, self.region)
        self.assertIsNotNone(vote.created_at)
        
    def test_vote_choices(self):
        """Test vote choices."""
        # Create votes with different choices
        yes_vote = PublicVote.objects.create(
            bill=self.bill,
            user=self.user2,
            vote=VoteChoices.YES,
            region=self.region
        )
        
        # Create a new bill for testing different votes
        bill2 = Bill.objects.create(
            bill_number='TEST-002',
            title='Test Bill 2',
            description='Another test bill',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='public_participation',
            bill_type='private'
        )
        
        no_vote = PublicVote.objects.create(
            bill=bill2,
            user=self.user,
            vote=VoteChoices.NO,
            region=self.region
        )
        
        abstain_vote = PublicVote.objects.create(
            bill=bill2,
            user=self.user2,
            vote=VoteChoices.ABSTAIN,
            region=self.region
        )
        
        self.assertEqual(yes_vote.vote, VoteChoices.YES)
        self.assertEqual(no_vote.vote, VoteChoices.NO)
        self.assertEqual(abstain_vote.vote, VoteChoices.ABSTAIN)
        
    def test_vote_unique_constraint(self):
        """Test that a user can only vote once per bill."""
        # Create a vote
        PublicVote.objects.create(
            bill=self.bill,
            user=self.user,
            vote=VoteChoices.YES,
            region=self.region
        )
        
        # Try to create another vote for the same user and bill
        with self.assertRaises(Exception):  # Could be IntegrityError or ValidationError
            PublicVote.objects.create(
                bill=self.bill,
                user=self.user,
                vote=VoteChoices.NO,  # Different vote
                region=self.region
            )
            
    def test_string_representation(self):
        """Test the string representation of a public vote."""
        vote = PublicVote.objects.create(
            bill=self.bill,
            user=self.user,
            vote=VoteChoices.YES,
            comment="Test comment",
            region=self.region
        )
        
        expected_string = f"{self.user.username} voted {VoteChoices.YES} on {self.bill.bill_number}"
        self.assertEqual(str(vote), expected_string)


class OfficialVoteModelTest(TestCase):
    """Test cases for the OfficialVote model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a user to act as proposer
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
        
        # Mock legislators
        self.legislator1 = MockLegislator(name="Legislator 1", id=1)
        self.legislator2 = MockLegislator(name="Legislator 2", id=2)
        
        # Get content type for User (as mock for legislator)
        self.content_type = ContentType.objects.get_for_model(User)
        
        # Create admin user for legislator
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='password123',
            is_staff=True
        )
        
    def test_create_official_vote(self):
        """Test creating an official vote."""
        vote = OfficialVote.objects.create(
            bill=self.bill,
            legislator_content_type=self.content_type,
            legislator_object_id=self.admin_user.id,
            vote=VoteChoices.YES,
            session_name="Test Session",
            reason="Test reason"
        )
        
        self.assertEqual(vote.bill, self.bill)
        self.assertEqual(vote.legislator_content_type, self.content_type)
        self.assertEqual(vote.legislator_object_id, self.admin_user.id)
        self.assertEqual(vote.vote, VoteChoices.YES)
        self.assertEqual(vote.session_name, "Test Session")
        self.assertEqual(vote.reason, "Test reason")
        self.assertIsNotNone(vote.timestamp)
        
    def test_vote_choices(self):
        """Test vote choices for official votes."""
        # Create votes with different choices
        yes_vote = OfficialVote.objects.create(
            bill=self.bill,
            legislator_content_type=self.content_type,
            legislator_object_id=1,  # Using ID directly
            vote=VoteChoices.YES,
            session_name="Test Session"
        )
        
        no_vote = OfficialVote.objects.create(
            bill=self.bill,
            legislator_content_type=self.content_type,
            legislator_object_id=2,  # Different legislator
            vote=VoteChoices.NO,
            session_name="Test Session"
        )
        
        abstain_vote = OfficialVote.objects.create(
            bill=self.bill,
            legislator_content_type=self.content_type,
            legislator_object_id=3,  # Different legislator
            vote=VoteChoices.ABSTAIN,
            session_name="Test Session"
        )
        
        self.assertEqual(yes_vote.vote, VoteChoices.YES)
        self.assertEqual(no_vote.vote, VoteChoices.NO)
        self.assertEqual(abstain_vote.vote, VoteChoices.ABSTAIN)
        
    def test_vote_unique_constraint(self):
        """Test that a legislator can only vote once per bill in a given session."""
        # Create a vote
        OfficialVote.objects.create(
            bill=self.bill,
            legislator_content_type=self.content_type,
            legislator_object_id=self.admin_user.id,
            vote=VoteChoices.YES,
            session_name="Test Session"
        )
        
        # Try to create another vote for the same legislator, bill, and session
        with self.assertRaises(Exception):  # Could be IntegrityError or ValidationError
            OfficialVote.objects.create(
                bill=self.bill,
                legislator_content_type=self.content_type,
                legislator_object_id=self.admin_user.id,
                vote=VoteChoices.NO,  # Different vote
                session_name="Test Session"  # Same session
            )
            
    def test_different_session_voting(self):
        """Test that a legislator can vote multiple times on the same bill in different sessions."""
        # Create a vote in one session
        OfficialVote.objects.create(
            bill=self.bill,
            legislator_content_type=self.content_type,
            legislator_object_id=self.admin_user.id,
            vote=VoteChoices.YES,
            session_name="First Reading"
        )
        
        # Create another vote in a different session - should succeed
        second_vote = OfficialVote.objects.create(
            bill=self.bill,
            legislator_content_type=self.content_type,
            legislator_object_id=self.admin_user.id,
            vote=VoteChoices.NO,  # Different vote
            session_name="Second Reading"  # Different session
        )
        
        self.assertEqual(second_vote.vote, VoteChoices.NO)
        self.assertEqual(second_vote.session_name, "Second Reading")
        
    def test_string_representation(self):
        """Test the string representation of an official vote."""
        vote = OfficialVote.objects.create(
            bill=self.bill,
            legislator_content_type=self.content_type,
            legislator_object_id=self.admin_user.id,
            vote=VoteChoices.YES,
            session_name="Test Session",
            reason="Test reason"
        )
        
        # Since we're using User as a mock for legislator, the string should contain the username
        expected_string = f"Official vote on {self.bill.bill_number} by {self.admin_user.username}: {VoteChoices.YES}"
        self.assertEqual(str(vote), expected_string) 