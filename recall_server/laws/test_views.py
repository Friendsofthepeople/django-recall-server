import json
from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from recall_server.laws.models import (
    Bill, BillRevision, BillAmendment, PublishedLaw, Comment
)


class BillViewsetTest(TestCase):
    """Test cases for the Bill API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        # Create a user for testing
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        # Authenticate
        self.client.force_authenticate(user=self.user)
        
        # Create another user for testing permissions
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
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
            is_draft=True
        )

    def test_list_bills(self):
        """Test listing bills."""
        url = reverse('bill-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_bill(self):
        """Test retrieving a bill."""
        url = reverse('bill-detail', kwargs={'pk': self.bill.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bill_number'], 'TEST-001')
        self.assertEqual(response.data['title'], 'Test Bill')

    def test_create_bill(self):
        """Test creating a bill."""
        url = reverse('bill-list')
        data = {
            'bill_number': 'TEST-002',
            'title': 'New Test Bill',
            'description': 'A new bill for testing',
            'sponsor': 'New Test Sponsor',
            'bill_type': 'private',
            'status': 'draft',
            'is_draft': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['bill_number'], 'TEST-002')
        self.assertEqual(response.data['title'], 'New Test Bill')
        self.assertEqual(response.data['proposer'], self.user.id)

    def test_update_bill(self):
        """Test updating a bill."""
        url = reverse('bill-detail', kwargs={'pk': self.bill.pk})
        data = {
            'title': 'Updated Test Bill',
            'description': 'An updated bill for testing'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Test Bill')
        self.assertEqual(response.data['description'], 'An updated bill for testing')

    def test_delete_bill(self):
        """Test deleting a bill."""
        url = reverse('bill-detail', kwargs={'pk': self.bill.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Bill.objects.count(), 0)

    def test_create_revision(self):
        """Test creating a revision for a bill."""
        url = reverse('bill-create-revision', kwargs={'pk': self.bill.pk})
        data = {
            'content': 'This is the content of the revision',
            'summary': 'This is a summary of the revision',
            'is_published': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is the content of the revision')
        self.assertEqual(response.data['summary'], 'This is a summary of the revision')
        self.assertEqual(response.data['version_number'], 1)
        self.assertEqual(response.data['created_by'], self.user.id)
        self.assertTrue(response.data['is_published'])
        
        # Check that the bill was updated with the current revision
        self.bill.refresh_from_db()
        self.assertIsNotNone(self.bill.current_revision)
        self.assertEqual(self.bill.current_revision.content, 'This is the content of the revision')

    def test_create_revision_missing_content(self):
        """Test creating a revision without content."""
        url = reverse('bill-create-revision', kwargs={'pk': self.bill.pk})
        data = {
            'summary': 'This is a summary of the revision',
            'is_published': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_publish_law(self):
        """Test publishing a bill as a law."""
        # Create a revision first
        revision = BillRevision.objects.create(
            bill=self.bill,
            version_number=1,
            content="Law content",
            summary="Law summary",
            created_by=self.user,
            stage='enacted',
            is_published=True
        )
        
        # Update bill
        self.bill.current_revision = revision
        self.bill.status = 'enacted'
        self.bill.save()
        
        # Publish the law
        url = reverse('bill-publish-law', kwargs={'pk': self.bill.pk})
        enactment_date = timezone.now().isoformat()
        effective_date = (timezone.now() + timedelta(days=30)).isoformat()
        data = {
            'law_number': 'TEST-LAW-001',
            'enactment_date': enactment_date,
            'effective_date': effective_date,
            'gazette_reference': 'GAZ-2023-001'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['law_number'], 'TEST-LAW-001')
        self.assertEqual(response.data['title'], self.bill.title)
        self.assertEqual(response.data['content'], revision.content)
        self.assertEqual(response.data['gazette_reference'], 'GAZ-2023-001')

    def test_publish_law_missing_fields(self):
        """Test publishing a law with missing fields."""
        # Create a revision first
        revision = BillRevision.objects.create(
            bill=self.bill,
            version_number=1,
            content="Law content",
            summary="Law summary",
            created_by=self.user,
            stage='enacted',
            is_published=True
        )
        
        # Update bill
        self.bill.current_revision = revision
        self.bill.status = 'enacted'
        self.bill.save()
        
        # Publish the law with missing fields
        url = reverse('bill-publish-law', kwargs={'pk': self.bill.pk})
        data = {
            'law_number': 'TEST-LAW-001'  # Missing enactment_date and effective_date
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_start_public_participation(self):
        """Test starting public participation for a bill."""
        url = reverse('bill-start-public-participation', kwargs={'pk': self.bill.pk})
        end_date = (timezone.now() + timedelta(days=30)).isoformat()
        data = {
            'end_date': end_date
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the bill was updated
        self.bill.refresh_from_db()
        self.assertIsNotNone(self.bill.public_participation_start)
        self.assertIsNotNone(self.bill.public_participation_end)
        self.assertTrue(self.bill.public_participation_active)

    def test_start_public_participation_missing_fields(self):
        """Test starting public participation without end_date."""
        url = reverse('bill-start-public-participation', kwargs={'pk': self.bill.pk})
        data = {}  # Missing end_date
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_end_public_participation(self):
        """Test ending public participation for a bill."""
        # First start public participation
        self.bill.start_public_participation(timezone.now() + timedelta(days=30))
        self.bill.save()
        
        url = reverse('bill-end-public-participation', kwargs={'pk': self.bill.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the bill was updated
        self.bill.refresh_from_db()
        self.assertIsNone(self.bill.public_participation_end)
        self.assertFalse(self.bill.public_participation_active)

    def test_refer_to_committee(self):
        """Test referring a bill to a committee."""
        url = reverse('bill-refer-to-committee', kwargs={'pk': self.bill.pk})
        data = {
            'committee_name': 'Test Committee'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the bill was updated
        self.bill.refresh_from_db()
        self.assertTrue(self.bill.referred_to_committee)
        self.assertEqual(self.bill.status, 'committee')

    def test_refer_to_committee_missing_fields(self):
        """Test referring a bill to a committee without committee_name."""
        url = reverse('bill-refer-to-committee', kwargs={'pk': self.bill.pk})
        data = {}  # Missing committee_name
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_committee_report(self):
        """Test adding a committee report to a bill."""
        # First refer the bill to a committee
        self.bill.refer_to_committee('Test Committee')
        self.bill.save()
        
        url = reverse('bill-add-committee-report', kwargs={'pk': self.bill.pk})
        data = {
            'report': 'This is a committee report',
            'recommendation': 'approve'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the bill was updated
        self.bill.refresh_from_db()
        self.assertEqual(self.bill.committee_report, 'This is a committee report')
        self.assertEqual(self.bill.committee_recommendation, 'approve')

    def test_add_committee_report_missing_fields(self):
        """Test adding a committee report without required fields."""
        # First refer the bill to a committee
        self.bill.refer_to_committee('Test Committee')
        self.bill.save()
        
        url = reverse('bill-add-committee-report', kwargs={'pk': self.bill.pk})
        data = {
            'report': 'This is a committee report'  # Missing recommendation
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_revisions(self):
        """Test retrieving revisions for a bill."""
        # Create some revisions
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
            stage='draft',
            is_published=False
        )
        
        # Get all revisions
        url = reverse('bill-revisions', kwargs={'pk': self.bill.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Get only published revisions
        url = reverse('bill-revisions', kwargs={'pk': self.bill.pk}) + '?published=true'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['version_number'], 1)

    def test_get_amendments(self):
        """Test retrieving amendments for a bill."""
        # Create some amendments
        amendment1 = BillAmendment.objects.create(
            bill=self.bill,
            title="Amendment 1",
            description="This is amendment 1",
            proposed_text="Amended text 1",
            section_reference="Section 1",
            proposed_by="MP",
            proposed_by_id=self.user.id,
            proposed_date=timezone.now(),
            status='pending'
        )
        
        amendment2 = BillAmendment.objects.create(
            bill=self.bill,
            title="Amendment 2",
            description="This is amendment 2",
            proposed_text="Amended text 2",
            section_reference="Section 2",
            proposed_by="MP",
            proposed_by_id=self.user.id,
            proposed_date=timezone.now(),
            status='approved'
        )
        
        # Get all amendments
        url = reverse('bill-amendments', kwargs={'pk': self.bill.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Get only pending amendments
        url = reverse('bill-amendments', kwargs={'pk': self.bill.pk}) + '?status=pending'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Amendment 1')
        
        # Get only approved amendments
        url = reverse('bill-amendments', kwargs={'pk': self.bill.pk}) + '?status=approved'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Amendment 2')


class BillRevisionViewsetTest(TestCase):
    """Test cases for the BillRevision API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        # Create a user for testing
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        # Authenticate
        self.client.force_authenticate(user=self.user)
        
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
        
        # Update bill with current revision
        self.bill.current_revision = self.revision
        self.bill.save()

    def test_list_revisions(self):
        """Test listing revisions."""
        url = reverse('billrevision-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_revision(self):
        """Test retrieving a revision."""
        url = reverse('billrevision-detail', kwargs={'pk': self.revision.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bill'], self.bill.id)
        self.assertEqual(response.data['version_number'], 1)
        self.assertEqual(response.data['content'], 'Revision content')

    def test_update_revision(self):
        """Test updating a revision."""
        url = reverse('billrevision-detail', kwargs={'pk': self.revision.pk})
        data = {
            'summary': 'Updated summary'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['summary'], 'Updated summary')

    def test_publish_revision(self):
        """Test publishing a revision."""
        # First unpublish the revision
        self.revision.is_published = False
        self.revision.save()
        
        url = reverse('billrevision-publish', kwargs={'pk': self.revision.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the revision was published
        self.revision.refresh_from_db()
        self.assertTrue(self.revision.is_published)

    def test_unpublish_revision(self):
        """Test unpublishing a revision."""
        url = reverse('billrevision-unpublish', kwargs={'pk': self.revision.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the revision was unpublished
        self.revision.refresh_from_db()
        self.assertFalse(self.revision.is_published)

    def test_filter_revisions_by_bill(self):
        """Test filtering revisions by bill."""
        # Create another bill and revision
        bill2 = Bill.objects.create(
            bill_number='TEST-002',
            title='Test Bill 2',
            description='Another bill for testing',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='draft',
            bill_type='private'
        )
        
        revision2 = BillRevision.objects.create(
            bill=bill2,
            version_number=1,
            content="Revision content for bill 2",
            summary="Revision summary for bill 2",
            created_by=self.user,
            stage='draft',
            is_published=True
        )
        
        # Filter by first bill
        url = reverse('billrevision-list') + f'?bill={self.bill.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['bill'], self.bill.id)
        
        # Filter by second bill
        url = reverse('billrevision-list') + f'?bill={bill2.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['bill'], bill2.id)

    def test_filter_revisions_by_published(self):
        """Test filtering revisions by published status."""
        # Create an unpublished revision
        revision2 = BillRevision.objects.create(
            bill=self.bill,
            version_number=2,
            content="Unpublished revision content",
            summary="Unpublished revision summary",
            created_by=self.user,
            stage='draft',
            is_published=False
        )
        
        # Filter by published=true
        url = reverse('billrevision-list') + '?published=true'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['version_number'], 1)
        
        # Filter by published=false
        url = reverse('billrevision-list') + '?published=false'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['version_number'], 2)


class BillAmendmentViewsetTest(TestCase):
    """Test cases for the BillAmendment API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        # Create a user for testing
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        # Authenticate
        self.client.force_authenticate(user=self.user)
        
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

    def test_list_amendments(self):
        """Test listing amendments."""
        url = reverse('billamendment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_amendment(self):
        """Test retrieving an amendment."""
        url = reverse('billamendment-detail', kwargs={'pk': self.amendment.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bill'], self.bill.id)
        self.assertEqual(response.data['title'], 'Test Amendment')
        self.assertEqual(response.data['proposed_text'], 'Amended text')

    def test_create_amendment(self):
        """Test creating an amendment."""
        url = reverse('billamendment-list')
        data = {
            'bill': self.bill.id,
            'title': 'New Amendment',
            'description': 'This is a new amendment',
            'proposed_text': 'New amended text',
            'section_reference': 'Section 2',
            'proposed_by': 'MP',
            'status': 'pending'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['bill'], self.bill.id)
        self.assertEqual(response.data['title'], 'New Amendment')
        self.assertEqual(response.data['proposed_by'], 'MP')
        self.assertEqual(response.data['proposed_by_id'], self.user.id)
        self.assertEqual(response.data['status'], 'pending')

    def test_update_amendment(self):
        """Test updating an amendment."""
        url = reverse('billamendment-detail', kwargs={'pk': self.amendment.pk})
        data = {
            'description': 'Updated amendment description'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated amendment description')

    def test_approve_amendment(self):
        """Test approving an amendment."""
        url = reverse('billamendment-approve', kwargs={'pk': self.amendment.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the amendment was approved
        self.amendment.refresh_from_db()
        self.assertEqual(self.amendment.status, 'approved')

    def test_reject_amendment(self):
        """Test rejecting an amendment."""
        url = reverse('billamendment-reject', kwargs={'pk': self.amendment.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the amendment was rejected
        self.amendment.refresh_from_db()
        self.assertEqual(self.amendment.status, 'rejected')

    def test_withdraw_amendment(self):
        """Test withdrawing an amendment."""
        url = reverse('billamendment-withdraw', kwargs={'pk': self.amendment.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the amendment was withdrawn
        self.amendment.refresh_from_db()
        self.assertEqual(self.amendment.status, 'withdrawn')

    def test_filter_amendments_by_bill(self):
        """Test filtering amendments by bill."""
        # Create another bill and amendment
        bill2 = Bill.objects.create(
            bill_number='TEST-002',
            title='Test Bill 2',
            description='Another bill for testing',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='draft',
            bill_type='private'
        )
        
        amendment2 = BillAmendment.objects.create(
            bill=bill2,
            title="Amendment for bill 2",
            description="This is an amendment for bill 2",
            proposed_text="Amended text for bill 2",
            section_reference="Section 1",
            proposed_by="MP",
            proposed_by_id=self.user.id,
            proposed_date=timezone.now(),
            status='pending'
        )
        
        # Filter by first bill
        url = reverse('billamendment-list') + f'?bill={self.bill.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['bill'], self.bill.id)
        
        # Filter by second bill
        url = reverse('billamendment-list') + f'?bill={bill2.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['bill'], bill2.id)

    def test_filter_amendments_by_status(self):
        """Test filtering amendments by status."""
        # Create amendments with different statuses
        amendment2 = BillAmendment.objects.create(
            bill=self.bill,
            title="Approved Amendment",
            description="This is an approved amendment",
            proposed_text="Approved amended text",
            section_reference="Section 2",
            proposed_by="MP",
            proposed_by_id=self.user.id,
            proposed_date=timezone.now(),
            status='approved'
        )
        
        amendment3 = BillAmendment.objects.create(
            bill=self.bill,
            title="Rejected Amendment",
            description="This is a rejected amendment",
            proposed_text="Rejected amended text",
            section_reference="Section 3",
            proposed_by="MP",
            proposed_by_id=self.user.id,
            proposed_date=timezone.now(),
            status='rejected'
        )
        
        # Filter by pending status
        url = reverse('billamendment-list') + '?status=pending'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'pending')
        
        # Filter by approved status
        url = reverse('billamendment-list') + '?status=approved'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'approved')
        
        # Filter by rejected status
        url = reverse('billamendment-list') + '?status=rejected'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'rejected')


class PublishedLawViewsetTest(TestCase):
    """Test cases for the PublishedLaw API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        # Create a user for testing
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        # Authenticate
        self.client.force_authenticate(user=self.user)
        
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
        
        # Update bill with current revision
        self.bill.current_revision = self.revision
        self.bill.save()
        
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

    def test_list_laws(self):
        """Test listing published laws."""
        url = reverse('publishedlaw-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_law(self):
        """Test retrieving a published law."""
        url = reverse('publishedlaw-detail', kwargs={'pk': self.law.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bill'], self.bill.id)
        self.assertEqual(response.data['title'], 'Test Bill')
        self.assertEqual(response.data['law_number'], 'LAW-001')
        self.assertEqual(response.data['content'], 'Law content')

    def test_filter_laws_by_bill(self):
        """Test filtering laws by bill."""
        # Create another bill and law
        bill2 = Bill.objects.create(
            bill_number='TEST-002',
            title='Test Bill 2',
            description='Another bill for testing',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='enacted',
            bill_type='private'
        )
        
        revision2 = BillRevision.objects.create(
            bill=bill2,
            version_number=1,
            content="Law content for bill 2",
            summary="Law summary for bill 2",
            created_by=self.user,
            stage='enacted',
            is_published=True
        )
        
        law2 = PublishedLaw.objects.create(
            bill=bill2,
            title=bill2.title,
            law_number="LAW-002",
            content=revision2.content,
            enactment_date=timezone.now(),
            effective_date=timezone.now() + timedelta(days=30),
            gazette_reference="GAZ-2023-002",
            final_revision=revision2
        )
        
        # Filter by first bill
        url = reverse('publishedlaw-list') + f'?bill={self.bill.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['bill'], self.bill.id)
        
        # Filter by second bill
        url = reverse('publishedlaw-list') + f'?bill={bill2.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['bill'], bill2.id)

    def test_filter_laws_by_enactment_date(self):
        """Test filtering laws by enactment date range."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        # Create laws with different enactment dates
        self.law.enactment_date = today
        self.law.save()
        
        # Filter by enactment date range including today
        url = reverse('publishedlaw-list') + f'?enactment_date_after={yesterday}&enactment_date_before={tomorrow}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Filter by enactment date range not including today
        url = reverse('publishedlaw-list') + f'?enactment_date_after={tomorrow}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_filter_laws_by_effective_date(self):
        """Test filtering laws by effective date range."""
        future_date = timezone.now().date() + timedelta(days=30)
        before_future = future_date - timedelta(days=1)
        after_future = future_date + timedelta(days=1)
        
        # Update law with specific effective date
        self.law.effective_date = future_date
        self.law.save()
        
        # Filter by effective date range including future_date
        url = reverse('publishedlaw-list') + f'?effective_date_after={before_future}&effective_date_before={after_future}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Filter by effective date range not including future_date
        url = reverse('publishedlaw-list') + f'?effective_date_after={after_future}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_search_laws(self):
        """Test searching for laws by number or title."""
        # Search by law number
        url = reverse('publishedlaw-list') + '?search=LAW-001'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Search by title
        url = reverse('publishedlaw-list') + '?search=Test Bill'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Search by non-matching term
        url = reverse('publishedlaw-list') + '?search=NonExistent'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0) 