from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils import timezone

from recall_server.voting.models import PublicVote, OfficialVote, VoteChoices
from recall_server.laws.models import Bill


class MockLegislator:
    """Mock class for legislator testing."""
    
    def __init__(self, name, id):
        self.name = name
        self.id = id


class VoteChoicesTest(TestCase):
    """Test cases for the VoteChoices model."""

    def test_vote_choices(self):
        """Test vote choices."""
        self.assertEqual(VoteChoices.YES, 'yes')
        self.assertEqual(VoteChoices.NO, 'no')
        self.assertEqual(VoteChoices.ABSTAIN, 'abstain')


class PublicVoteTest(TestCase):
    """Test cases for the PublicVote model."""

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
        
        # Mock a region/county - this would normally come from county app
        # For this test, we'll mock the County model since we can't import it
        class MockCounty:
            def __init__(self, id, name):
                self.id = id
                self.name = name
                
            def save(self, *args, **kwargs):
                pass
                
        self.region = MockCounty(1, "Test County")
        
        # Monkey patch the bill to allow voting
        def can_be_voted():
            return True
        self.bill.can_be_voted = can_be_voted
        
    def test_public_vote_creation(self):
        """Test creating a public vote."""
        vote = PublicVote(
            bill=self.bill,
            user=self.user,
            vote=VoteChoices.YES,
            comment="Test comment",
            region=self.region
        )
        vote.save()
        
        self.assertEqual(vote.bill, self.bill)
        self.assertEqual(vote.user, self.user)
        self.assertEqual(vote.vote, VoteChoices.YES)
        self.assertEqual(vote.comment, "Test comment")
        self.assertEqual(vote.region, self.region)
        self.assertIsNotNone(vote.date)
        
    def test_public_vote_str(self):
        """Test the string representation of a public vote."""
        vote = PublicVote(
            bill=self.bill,
            user=self.user,
            vote=VoteChoices.YES,
            region=self.region
        )
        self.assertEqual(str(vote), f"{self.user}: {self.bill} {VoteChoices.YES}")
        
    def test_public_vote_unique_constraint(self):
        """Test that a user can only vote once per bill."""
        # Create a vote
        vote1 = PublicVote(
            bill=self.bill,
            user=self.user,
            vote=VoteChoices.YES,
            region=self.region
        )
        vote1.save()
        
        # Try to create another vote from same user for same bill
        vote2 = PublicVote(
            bill=self.bill,
            user=self.user,
            vote=VoteChoices.NO,
            region=self.region
        )
        
        # This should raise a unique constraint violation
        with self.assertRaises(Exception):
            vote2.save()
            
    def test_public_vote_validation(self):
        """Test that votes are only allowed on bills that can be voted on."""
        # Monkey patch the bill to disallow voting
        def cannot_be_voted():
            return False
        self.bill.can_be_voted = cannot_be_voted
        
        # Try to create a vote
        vote = PublicVote(
            bill=self.bill,
            user=self.user,
            vote=VoteChoices.YES,
            region=self.region
        )
        
        # This should raise a validation error
        with self.assertRaises(ValidationError):
            vote.save()


class OfficialVoteTest(TestCase):
    """Test cases for the OfficialVote model."""

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
        
    def test_official_vote_creation(self):
        """Test creating an official vote."""
        vote = OfficialVote(
            bill=self.bill,
            legislator_content_type=self.content_type,
            legislator_object_id=self.legislator.id,
            vote=VoteChoices.YES,
            session_name="Test Session",
            reason="Test reason"
        )
        vote.save()
        
        self.assertEqual(vote.bill, self.bill)
        self.assertEqual(vote.legislator_content_type, self.content_type)
        self.assertEqual(vote.legislator_object_id, self.legislator.id)
        self.assertEqual(vote.vote, VoteChoices.YES)
        self.assertEqual(vote.session_name, "Test Session")
        self.assertEqual(vote.reason, "Test reason")
        self.assertIsNotNone(vote.date)
        
    def test_official_vote_str(self):
        """Test the string representation of an official vote."""
        # Create a vote
        vote = OfficialVote(
            bill=self.bill,
            legislator_content_type=self.content_type,
            legislator_object_id=self.legislator.id,
            vote=VoteChoices.YES
        )
        
        # Set the legislator dynamically since we can't set it directly
        # in the constructor with GenericForeignKey
        vote.legislator = self.legislator
        
        self.assertEqual(str(vote), f"{self.legislator}: {self.bill} - {VoteChoices.YES}")
        
    def test_official_vote_unique_constraint(self):
        """Test that a legislator can only vote once per bill."""
        # Create a vote
        vote1 = OfficialVote(
            bill=self.bill,
            legislator_content_type=self.content_type,
            legislator_object_id=self.legislator.id,
            vote=VoteChoices.YES
        )
        vote1.save()
        
        # Try to create another vote from same legislator for same bill
        vote2 = OfficialVote(
            bill=self.bill,
            legislator_content_type=self.content_type,
            legislator_object_id=self.legislator.id,
            vote=VoteChoices.NO
        )
        
        # This should raise a unique constraint violation
        with self.assertRaises(Exception):
            vote2.save()
            
    def test_get_legislator_name(self):
        """Test getting the legislator name."""
        vote = OfficialVote(
            bill=self.bill,
            legislator_content_type=self.content_type,
            legislator_object_id=self.legislator.id,
            vote=VoteChoices.YES
        )
        vote.legislator = self.legislator
        
        self.assertEqual(vote.get_legislator_name(), "Test Legislator")
        
    def test_get_legislator_type(self):
        """Test getting the legislator type."""
        vote = OfficialVote(
            bill=self.bill,
            legislator_content_type=self.content_type,
            legislator_object_id=self.legislator.id,
            vote=VoteChoices.YES
        )
        
        # Should capitalize the model name from content type
        self.assertEqual(vote.get_legislator_type(), "User")
