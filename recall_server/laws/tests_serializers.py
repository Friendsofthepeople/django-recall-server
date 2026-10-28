import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from recall_server.laws.models import (
    Bill, BillRevision, BillAmendment, PublishedLaw, Comment
)
from recall_server.laws.serializers import (
    BillSerializer, BillDetailSerializer, CommentSerializer,
    BillRevisionSerializer, BillRevisionDetailSerializer,
    BillAmendmentSerializer, PublishedLawSerializer, PublishedLawDetailSerializer
)


class BillSerializerTest(TestCase):
    """Test cases for the Bill serializers."""

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
            description='A bill for testing',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='draft',
            bill_type='private',
            is_draft=True,
            created_at=timezone.now()
        )

    def test_bill_serializer(self):
        """Test the BillSerializer."""
        serializer = BillSerializer(self.bill)
        
        # Test basic fields
        self.assertEqual(serializer.data['bill_number'], 'TEST-001')
        self.assertEqual(serializer.data['title'], 'Test Bill')
        self.assertEqual(serializer.data['description'], 'A bill for testing')
        self.assertEqual(serializer.data['sponsor'], 'Test Sponsor')
        self.assertEqual(serializer.data['proposer'], self.user.id)
        self.assertEqual(serializer.data['status'], 'draft')
        self.assertEqual(serializer.data['bill_type'], 'private')
        self.assertTrue(serializer.data['is_draft'])
        
        # Test calculated fields
        self.assertEqual(serializer.data['current_revision_number'], None)
        self.assertEqual(serializer.data['revisions_count'], 0)
        self.assertEqual(serializer.data['amendments_count'], 0)
        self.assertFalse(serializer.data['public_participation_active'])
        self.assertFalse(serializer.data['is_published_as_law'])
        
    def test_bill_serializer_with_revisions(self):
        """Test the BillSerializer with revisions."""
        # Create revisions
        revision1 = BillRevision.objects.create(
            bill=self.bill,
            version_number=1,
            content="Revision 1 content",
            summary="Revision 1 summary",
            created_by=self.user,
            stage='draft',
            is_published=True
        )
        
        revision2 = BillRevision.objects.create(
            bill=self.bill,
            version_number=2,
            content="Revision 2 content",
            summary="Revision 2 summary",
            created_by=self.user,
            stage='review',
            is_published=True
        )
        
        # Update bill with current revision
        self.bill.current_revision = revision2
        self.bill.save()
        
        # Test serializer
        serializer = BillSerializer(self.bill)
        self.assertEqual(serializer.data['current_revision_number'], 2)
        self.assertEqual(serializer.data['revisions_count'], 2)
        
    def test_bill_serializer_with_amendments(self):
        """Test the BillSerializer with amendments."""
        # Create an amendment
        amendment = BillAmendment.objects.create(
            bill=self.bill,
            title="Test Amendment",
            description="This is a test amendment",
            proposed_text="Amended text",
            section_reference="Section 1",
            proposed_by="MP",
            proposed_by_id=self.user.id,
            proposed_date=timezone.now(),
            status='pending'
        )
        
        # Test serializer
        serializer = BillSerializer(self.bill)
        self.assertEqual(serializer.data['amendments_count'], 1)
        
    def test_bill_serializer_with_public_participation(self):
        """Test the BillSerializer with public participation."""
        # Start public participation
        start_date = timezone.now()
        end_date = start_date + datetime.timedelta(days=30)
        self.bill.public_participation_start = start_date
        self.bill.public_participation_end = end_date
        self.bill.save()
        
        # Test serializer
        serializer = BillSerializer(self.bill)
        self.assertTrue(serializer.data['public_participation_active'])
        
    def test_bill_serializer_with_published_law(self):
        """Test the BillSerializer with a published law."""
        # Create a revision
        revision = BillRevision.objects.create(
            bill=self.bill,
            version_number=1,
            content="Law content",
            summary="Law summary",
            created_by=self.user,
            stage='enacted',
            is_published=True
        )
        
        # Set bill as enacted
        self.bill.status = 'enacted'
        self.bill.save()
        
        # Create a published law
        law = PublishedLaw.objects.create(
            bill=self.bill,
            title=self.bill.title,
            law_number="LAW-001",
            content=revision.content,
            enactment_date=timezone.now(),
            effective_date=timezone.now() + datetime.timedelta(days=30),
            gazette_reference="GAZ-2023-001",
            final_revision=revision
        )
        
        # Test serializer
        serializer = BillSerializer(self.bill)
        self.assertTrue(serializer.data['is_published_as_law'])
        
    def test_bill_detail_serializer(self):
        """Test the BillDetailSerializer."""
        # Create a revision
        revision = BillRevision.objects.create(
            bill=self.bill,
            version_number=1,
            content="Revision content",
            summary="Revision summary",
            created_by=self.user,
            stage='draft',
            is_published=True
        )
        
        # Update bill with current revision
        self.bill.current_revision = revision
        self.bill.committee_report = "Committee report"
        self.bill.committee_recommendation = "approve"
        self.bill.save()
        
        # Create a comment
        comment = Comment.objects.create(
            bill=self.bill,
            user=self.user,
            content="This is a test comment",
            section_reference="Section 1"
        )
        
        # Test serializer
        serializer = BillDetailSerializer(self.bill)
        
        # Test basic fields (same as BillSerializer)
        self.assertEqual(serializer.data['bill_number'], 'TEST-001')
        self.assertEqual(serializer.data['title'], 'Test Bill')
        
        # Test additional fields
        self.assertIn('comments', serializer.data)
        self.assertEqual(len(serializer.data['comments']), 1)
        self.assertEqual(serializer.data['comments'][0]['content'], "This is a test comment")
        
        self.assertEqual(serializer.data['committee_report'], "Committee report")
        self.assertEqual(serializer.data['committee_recommendation'], "approve")
        
        self.assertIn('current_revision', serializer.data)
        self.assertEqual(serializer.data['current_revision']['version_number'], 1)
        self.assertEqual(serializer.data['current_revision']['content'], "Revision content")


class CommentSerializerTest(TestCase):
    """Test cases for the Comment serializer."""

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
            description='A bill for testing',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='draft',
            bill_type='private'
        )
        
        # Create a comment
        self.comment = Comment.objects.create(
            bill=self.bill,
            user=self.user,
            content="This is a test comment",
            section_reference="Section 1"
        )

    def test_comment_serializer(self):
        """Test the CommentSerializer."""
        serializer = CommentSerializer(self.comment)
        
        self.assertEqual(serializer.data['bill'], self.bill.id)
        self.assertEqual(serializer.data['user'], self.user.id)
        self.assertEqual(serializer.data['content'], "This is a test comment")
        self.assertEqual(serializer.data['section_reference'], "Section 1")
        self.assertIn('created_at', serializer.data)
        
        # Test user fields
        self.assertEqual(serializer.data['user_full_name'], 'testuser')
        
    def test_comment_create(self):
        """Test creating a comment through the serializer."""
        data = {
            'bill': self.bill.id,
            'user': self.user.id,
            'content': "This is a new comment",
            'section_reference': "Section 2"
        }
        
        serializer = CommentSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        comment = serializer.save()
        
        self.assertEqual(comment.bill, self.bill)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.content, "This is a new comment")
        self.assertEqual(comment.section_reference, "Section 2")


class BillRevisionSerializerTest(TestCase):
    """Test cases for the BillRevision serializers."""

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
            description='A bill for testing',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='draft',
            bill_type='private'
        )
        
        # Create a revision
        self.revision = BillRevision.objects.create(
            bill=self.bill,
            version_number=1,
            content="Revision content",
            summary="Revision summary",
            created_by=self.user,
            stage='draft',
            is_published=True,
            created_at=timezone.now()
        )

    def test_bill_revision_serializer(self):
        """Test the BillRevisionSerializer."""
        serializer = BillRevisionSerializer(self.revision)
        
        self.assertEqual(serializer.data['bill'], self.bill.id)
        self.assertEqual(serializer.data['version_number'], 1)
        self.assertEqual(serializer.data['content'], "Revision content")
        self.assertEqual(serializer.data['summary'], "Revision summary")
        self.assertEqual(serializer.data['created_by'], self.user.id)
        self.assertEqual(serializer.data['stage'], 'draft')
        self.assertTrue(serializer.data['is_published'])
        self.assertIn('created_at', serializer.data)
        self.assertIn('revision_id', serializer.data)
        
    def test_bill_revision_detail_serializer(self):
        """Test the BillRevisionDetailSerializer."""
        # Create an amendment
        amendment = BillAmendment.objects.create(
            bill=self.bill,
            title="Test Amendment",
            description="This is a test amendment",
            proposed_text="Amended text",
            section_reference="Section 1",
            proposed_by="MP",
            proposed_by_id=self.user.id,
            proposed_date=timezone.now(),
            status='approved'
        )
        
        serializer = BillRevisionDetailSerializer(self.revision)
        
        # Test basic fields (same as BillRevisionSerializer)
        self.assertEqual(serializer.data['bill'], self.bill.id)
        self.assertEqual(serializer.data['version_number'], 1)
        self.assertEqual(serializer.data['content'], "Revision content")
        
        # Test incorporated amendments
        self.assertIn('incorporated_amendments', serializer.data)
        # Note: In a real situation, amendments would be related to revisions
        # This test just checks that the field exists


class BillAmendmentSerializerTest(TestCase):
    """Test cases for the BillAmendment serializer."""

    def setUp(self):
        """Set up test data."""
        # Create a user for testing
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        
        # Create a bill
        self.bill = Bill.objects.create(
            bill_number='TEST-001',
            title='Test Bill',
            description='A bill for testing',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='draft',
            bill_type='private'
        )
        
        # Create an amendment
        self.amendment = BillAmendment.objects.create(
            bill=self.bill,
            title="Test Amendment",
            description="This is a test amendment",
            proposed_text="Amended text",
            section_reference="Section 1",
            proposed_by="MP",
            proposed_by_id=self.user.id,
            proposed_date=timezone.now(),
            status='pending',
            votes_for=10,
            votes_against=5,
            votes_abstain=2
        )

    def test_amendment_serializer(self):
        """Test the BillAmendmentSerializer."""
        serializer = BillAmendmentSerializer(self.amendment)
        
        self.assertEqual(serializer.data['bill'], self.bill.id)
        self.assertEqual(serializer.data['title'], "Test Amendment")
        self.assertEqual(serializer.data['description'], "This is a test amendment")
        self.assertEqual(serializer.data['proposed_text'], "Amended text")
        self.assertEqual(serializer.data['section_reference'], "Section 1")
        self.assertEqual(serializer.data['proposed_by'], "MP")
        self.assertEqual(serializer.data['proposed_by_id'], self.user.id)
        self.assertEqual(serializer.data['status'], 'pending')
        self.assertEqual(serializer.data['votes_for'], 10)
        self.assertEqual(serializer.data['votes_against'], 5)
        self.assertEqual(serializer.data['votes_abstain'], 2)
        self.assertEqual(serializer.data['total_votes'], 17)
        
        # Test proposer name
        self.assertEqual(serializer.data['proposer_name'], 'Test User')
        
    def test_amendment_create(self):
        """Test creating an amendment through the serializer."""
        data = {
            'bill': self.bill.id,
            'title': "New Amendment",
            'description': "This is a new amendment",
            'proposed_text': "New amended text",
            'section_reference': "Section 2",
            'proposed_by': "MP",
            'proposed_by_id': self.user.id,
            'status': 'pending'
        }
        
        serializer = BillAmendmentSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        amendment = serializer.save()
        
        self.assertEqual(amendment.bill, self.bill)
        self.assertEqual(amendment.title, "New Amendment")
        self.assertEqual(amendment.description, "This is a new amendment")
        self.assertEqual(amendment.proposed_by, "MP")
        self.assertEqual(amendment.status, 'pending')


class PublishedLawSerializerTest(TestCase):
    """Test cases for the PublishedLaw serializers."""

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
            description='A bill for testing',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='enacted',
            bill_type='private'
        )
        
        # Create a revision
        self.revision = BillRevision.objects.create(
            bill=self.bill,
            version_number=1,
            content="Law content",
            summary="Law summary",
            created_by=self.user,
            stage='enacted',
            is_published=True
        )
        
        # Create a published law
        self.law = PublishedLaw.objects.create(
            bill=self.bill,
            title=self.bill.title,
            law_number="LAW-001",
            content=self.revision.content,
            enactment_date=timezone.now(),
            effective_date=timezone.now() + datetime.timedelta(days=30),
            gazette_reference="GAZ-2023-001",
            final_revision=self.revision
        )

    def test_published_law_serializer(self):
        """Test the PublishedLawSerializer."""
        serializer = PublishedLawSerializer(self.law)
        
        self.assertEqual(serializer.data['bill'], self.bill.id)
        self.assertEqual(serializer.data['title'], 'Test Bill')
        self.assertEqual(serializer.data['law_number'], "LAW-001")
        self.assertEqual(serializer.data['content'], "Law content")
        self.assertIn('enactment_date', serializer.data)
        self.assertIn('effective_date', serializer.data)
        self.assertEqual(serializer.data['gazette_reference'], "GAZ-2023-001")
        
        # Test bill_number field
        self.assertEqual(serializer.data['bill_number'], 'TEST-001')
        
    def test_published_law_detail_serializer(self):
        """Test the PublishedLawDetailSerializer."""
        serializer = PublishedLawDetailSerializer(self.law)
        
        # Test basic fields (same as PublishedLawSerializer)
        self.assertEqual(serializer.data['bill'], self.bill.id)
        self.assertEqual(serializer.data['title'], 'Test Bill')
        self.assertEqual(serializer.data['law_number'], "LAW-001")
        
        # Test final_revision field
        self.assertIn('final_revision', serializer.data)
        self.assertEqual(serializer.data['final_revision']['version_number'], 1)
        self.assertEqual(serializer.data['final_revision']['content'], "Law content") 