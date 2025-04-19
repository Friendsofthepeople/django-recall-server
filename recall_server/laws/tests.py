import os
from datetime import timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from recall_server.laws.models import (
    Bill, BillRevision, BillAmendment, PublishedLaw, Comment
)


class BillModelTest(TestCase):
    """Test cases for the Bill model."""

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
        )

    def test_bill_creation(self):
        """Test creating a Bill."""
        self.assertEqual(str(self.bill), 'TEST-001: Test Bill')
        self.assertEqual(self.bill.bill_number, 'TEST-001')
        self.assertEqual(self.bill.title, 'Test Bill')
        self.assertEqual(self.bill.description, 'A bill for testing')
        self.assertEqual(self.bill.sponsor, 'Test Sponsor')
        self.assertEqual(self.bill.proposer, self.user)
        self.assertEqual(self.bill.status, 'draft')
        self.assertEqual(self.bill.bill_type, 'private')
        self.assertTrue(self.bill.is_draft)
        self.assertIsNone(self.bill.current_revision)
        self.assertFalse(self.bill.referred_to_committee)
        self.assertIsNone(self.bill.committee_report)
        self.assertIsNone(self.bill.committee_recommendation)
        self.assertIsNone(self.bill.public_participation_start)
        self.assertIsNone(self.bill.public_participation_end)

    def test_create_revision(self):
        """Test creating a revision for a bill."""
        content = "This is the content of the test bill"
        summary = "This is a summary of the revision"
        
        # Create a revision
        revision = self.bill.create_revision(
            content=content,
            summary=summary,
            created_by=self.user,
            is_published=True
        )
        
        # Refresh the bill from the database
        self.bill.refresh_from_db()
        
        # Check that the revision was created correctly
        self.assertEqual(revision.bill, self.bill)
        self.assertEqual(revision.content, content)
        self.assertEqual(revision.summary, summary)
        self.assertEqual(revision.created_by, self.user)
        self.assertEqual(revision.version_number, 1)
        self.assertTrue(revision.is_published)
        self.assertEqual(revision.stage, 'draft')
        
        # Check that the bill was updated with the current revision
        self.assertEqual(self.bill.current_revision, revision)

    def test_multiple_revisions(self):
        """Test creating multiple revisions for a bill."""
        # Create first revision
        first_revision = self.bill.create_revision(
            content="First revision content",
            summary="First revision summary",
            created_by=self.user,
            is_published=True
        )
        
        # Create second revision
        second_revision = self.bill.create_revision(
            content="Second revision content",
            summary="Second revision summary",
            created_by=self.user,
            is_published=True
        )
        
        # Refresh the bill from the database
        self.bill.refresh_from_db()
        
        # Check that both revisions were created correctly
        self.assertEqual(first_revision.version_number, 1)
        self.assertEqual(second_revision.version_number, 2)
        
        # Check that the bill was updated with the current revision
        self.assertEqual(self.bill.current_revision, second_revision)

    def test_public_participation(self):
        """Test public participation methods."""
        # Test start_public_participation
        end_date = timezone.now() + timedelta(days=30)
        self.bill.start_public_participation(end_date)
        
        # Refresh the bill from the database
        self.bill.refresh_from_db()
        
        # Check that public participation was started correctly
        self.assertIsNotNone(self.bill.public_participation_start)
        self.assertEqual(self.bill.public_participation_end, end_date)
        self.assertTrue(self.bill.public_participation_active)
        
        # Test end_public_participation
        self.bill.end_public_participation()
        
        # Refresh the bill from the database
        self.bill.refresh_from_db()
        
        # Check that public participation was ended correctly
        self.assertIsNone(self.bill.public_participation_end)
        self.assertFalse(self.bill.public_participation_active)

    def test_committee_referral(self):
        """Test referring a bill to a committee."""
        committee_name = "Test Committee"
        self.bill.refer_to_committee(committee_name)
        
        # Refresh the bill from the database
        self.bill.refresh_from_db()
        
        # Check that the bill was referred correctly
        self.assertTrue(self.bill.referred_to_committee)
        self.assertEqual(self.bill.status, 'committee')
        
        # Test adding a committee report
        report = "Committee report content"
        recommendation = "approve"
        self.bill.add_committee_report(report, recommendation)
        
        # Refresh the bill from the database
        self.bill.refresh_from_db()
        
        # Check that the committee report was added correctly
        self.assertEqual(self.bill.committee_report, report)
        self.assertEqual(self.bill.committee_recommendation, recommendation)

    def test_publish_law(self):
        """Test publishing a bill as a law."""
        # Create a revision first
        revision = self.bill.create_revision(
            content="Law content",
            summary="Law summary",
            created_by=self.user,
            is_published=True
        )
        
        # Set the bill to be enacted
        self.bill.status = 'enacted'
        self.bill.save()
        
        # Publish the law
        law_number = "TEST-LAW-001"
        enactment_date = timezone.now()
        effective_date = timezone.now() + timedelta(days=30)
        gazette_ref = "GAZ-2023-001"
        
        law = self.bill.publish_law(
            law_number=law_number,
            enactment_date=enactment_date,
            effective_date=effective_date,
            gazette_reference=gazette_ref
        )
        
        # Check that the law was published correctly
        self.assertEqual(law.bill, self.bill)
        self.assertEqual(law.law_number, law_number)
        self.assertEqual(law.title, self.bill.title)
        self.assertEqual(law.content, revision.content)
        self.assertEqual(law.enactment_date, enactment_date)
        self.assertEqual(law.effective_date, effective_date)
        self.assertEqual(law.gazette_reference, gazette_ref)
        self.assertEqual(law.final_revision, revision)


class BillRevisionModelTest(TestCase):
    """Test cases for the BillRevision model."""

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
            is_published=True
        )

    def test_revision_creation(self):
        """Test creating a BillRevision."""
        self.assertEqual(str(self.revision), 'TEST-001: Version 1')
        self.assertEqual(self.revision.bill, self.bill)
        self.assertEqual(self.revision.version_number, 1)
        self.assertEqual(self.revision.content, "Revision content")
        self.assertEqual(self.revision.summary, "Revision summary")
        self.assertEqual(self.revision.created_by, self.user)
        self.assertEqual(self.revision.stage, 'draft')
        self.assertTrue(self.revision.is_published)

    def test_revision_publish_unpublish(self):
        """Test publishing and unpublishing a revision."""
        # Test unpublishing
        self.revision.unpublish()
        self.assertFalse(self.revision.is_published)
        
        # Test publishing
        self.revision.publish()
        self.assertTrue(self.revision.is_published)


class BillAmendmentModelTest(TestCase):
    """Test cases for the BillAmendment model."""

    def setUp(self):
        """Set up test data."""
        # Create users for testing
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
            status='pending'
        )

    def test_amendment_creation(self):
        """Test creating a BillAmendment."""
        self.assertEqual(str(self.amendment), 'Test Amendment')
        self.assertEqual(self.amendment.bill, self.bill)
        self.assertEqual(self.amendment.title, "Test Amendment")
        self.assertEqual(self.amendment.description, "This is a test amendment")
        self.assertEqual(self.amendment.proposed_text, "Amended text")
        self.assertEqual(self.amendment.section_reference, "Section 1")
        self.assertEqual(self.amendment.proposed_by, "MP")
        self.assertEqual(self.amendment.proposed_by_id, self.user.id)
        self.assertEqual(self.amendment.status, 'pending')
        self.assertEqual(self.amendment.votes_for, 0)
        self.assertEqual(self.amendment.votes_against, 0)
        self.assertEqual(self.amendment.votes_abstain, 0)

    def test_amendment_status_changes(self):
        """Test changing the status of an amendment."""
        # Test approving
        self.amendment.approve()
        self.assertEqual(self.amendment.status, 'approved')
        
        # Test rejecting
        self.amendment.reject()
        self.assertEqual(self.amendment.status, 'rejected')
        
        # Test withdrawing
        self.amendment.withdraw()
        self.assertEqual(self.amendment.status, 'withdrawn')

    def test_amendment_voting(self):
        """Test voting on an amendment."""
        # Add votes for
        self.amendment.add_vote('for')
        self.assertEqual(self.amendment.votes_for, 1)
        
        # Add votes against
        self.amendment.add_vote('against')
        self.assertEqual(self.amendment.votes_against, 1)
        
        # Add abstentions
        self.amendment.add_vote('abstain')
        self.assertEqual(self.amendment.votes_abstain, 1)
        
        # Test total votes
        self.assertEqual(self.amendment.total_votes, 3)


class PublishedLawModelTest(TestCase):
    """Test cases for the PublishedLaw model."""

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
            effective_date=timezone.now() + timedelta(days=30),
            gazette_reference="GAZ-2023-001",
            final_revision=self.revision
        )

    def test_law_creation(self):
        """Test creating a PublishedLaw."""
        self.assertEqual(str(self.law), 'LAW-001: Test Bill')
        self.assertEqual(self.law.bill, self.bill)
        self.assertEqual(self.law.title, 'Test Bill')
        self.assertEqual(self.law.law_number, "LAW-001")
        self.assertEqual(self.law.content, "Law content")
        self.assertIsNotNone(self.law.enactment_date)
        self.assertIsNotNone(self.law.effective_date)
        self.assertEqual(self.law.gazette_reference, "GAZ-2023-001")
        self.assertEqual(self.law.final_revision, self.revision)

    def test_pdf_document(self):
        """Test adding a PDF document to a law."""
        # Create a simple PDF file
        pdf_content = b'%PDF-1.4\n%Fake PDF content'
        pdf_file = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")
        
        # Add the PDF to the law
        self.law.pdf_document = pdf_file
        self.law.save()
        
        # Check that the PDF was saved correctly
        self.assertTrue(self.law.pdf_document.name.endswith('.pdf'))


class CommentModelTest(TestCase):
    """Test cases for the Comment model."""

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

    def test_comment_creation(self):
        """Test creating a Comment."""
        self.assertEqual(str(self.comment), f'Comment by {self.user.username} on {self.bill.bill_number}')
        self.assertEqual(self.comment.bill, self.bill)
        self.assertEqual(self.comment.user, self.user)
        self.assertEqual(self.comment.content, "This is a test comment")
        self.assertEqual(self.comment.section_reference, "Section 1")
        self.assertIsNotNone(self.comment.created_at)

    def tearDown(self):
        """Clean up after tests."""
        # Remove any PDF files created during testing
        for law in PublishedLaw.objects.all():
            if law.pdf_document:
                if os.path.isfile(law.pdf_document.path):
                    os.remove(law.pdf_document.path)
