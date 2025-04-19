from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
import datetime

from recall_server.mp.models import MP, MPAttendance, MPContribution
from recall_server.county.models import County, SubCounty


class MPModelTest(TestCase):
    """Test cases for the MP model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a county and subcounty
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
        
        # Create an MP
        self.mp = MP.objects.create(
            name="Test MP",
            subcounty=self.subcounty,
            party="Test Party",
            phone_number="1234567890",
            email="mp@example.com",
            bio="Test bio",
            education="Test education",
            experience="Test experience",
            election_date=timezone.now().date()
        )
        
    def test_mp_creation(self):
        """Test creating an MP object."""
        self.assertEqual(self.mp.name, "Test MP")
        self.assertEqual(self.mp.subcounty, self.subcounty)
        self.assertEqual(self.mp.party, "Test Party")
        self.assertEqual(self.mp.phone_number, "1234567890")
        self.assertEqual(self.mp.email, "mp@example.com")
        self.assertEqual(self.mp.bio, "Test bio")
        self.assertEqual(self.mp.education, "Test education")
        self.assertEqual(self.mp.experience, "Test experience")
        self.assertIsNotNone(self.mp.election_date)
        
    def test_string_representation(self):
        """Test string representation of an MP."""
        self.assertEqual(str(self.mp), "Test MP - Test SubCounty")
        
    def test_subcounty_relationship(self):
        """Test relationship with subcounty."""
        self.assertEqual(self.mp.subcounty.name, "Test SubCounty")
        
    def test_county_access(self):
        """Test accessing county through subcounty."""
        self.assertEqual(self.mp.subcounty.county.name, "Test County")


class MPAttendanceModelTest(TestCase):
    """Test cases for the MPAttendance model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a county and subcounty
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
        
        # Create an MP
        self.mp = MP.objects.create(
            name="Test MP",
            subcounty=self.subcounty,
            party="Test Party",
            phone_number="1234567890",
            email="mp@example.com",
            bio="Test bio",
            education="Test education",
            experience="Test experience",
            election_date=timezone.now().date()
        )
        
        # Create an attendance record
        self.attendance = MPAttendance.objects.create(
            mp=self.mp,
            date=timezone.now().date(),
            session_type="Parliament Session",
            status="present",
            notes="Test notes"
        )
        
    def test_attendance_creation(self):
        """Test creating an attendance record."""
        self.assertEqual(self.attendance.mp, self.mp)
        self.assertIsNotNone(self.attendance.date)
        self.assertEqual(self.attendance.session_type, "Parliament Session")
        self.assertEqual(self.attendance.status, "present")
        self.assertEqual(self.attendance.notes, "Test notes")
        
    def test_string_representation(self):
        """Test string representation of an attendance record."""
        expected = f"{self.mp.name} - {self.attendance.date} - {self.attendance.status}"
        self.assertEqual(str(self.attendance), expected)
        
    def test_mp_relationship(self):
        """Test relationship with MP."""
        self.assertEqual(self.attendance.mp.name, "Test MP")


class MPContributionModelTest(TestCase):
    """Test cases for the MPContribution model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a county and subcounty
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
        
        # Create an MP
        self.mp = MP.objects.create(
            name="Test MP",
            subcounty=self.subcounty,
            party="Test Party",
            phone_number="1234567890",
            email="mp@example.com",
            bio="Test bio",
            education="Test education",
            experience="Test experience",
            election_date=timezone.now().date()
        )
        
        # Create a contribution record
        self.contribution = MPContribution.objects.create(
            mp=self.mp,
            date=timezone.now().date(),
            title="Test Contribution",
            description="Test description",
            contribution_type="Bill",
            url="https://example.com/contribution",
            impact_score=8
        )
        
    def test_contribution_creation(self):
        """Test creating a contribution record."""
        self.assertEqual(self.contribution.mp, self.mp)
        self.assertIsNotNone(self.contribution.date)
        self.assertEqual(self.contribution.title, "Test Contribution")
        self.assertEqual(self.contribution.description, "Test description")
        self.assertEqual(self.contribution.contribution_type, "Bill")
        self.assertEqual(self.contribution.url, "https://example.com/contribution")
        self.assertEqual(self.contribution.impact_score, 8)
        
    def test_string_representation(self):
        """Test string representation of a contribution record."""
        expected = f"{self.mp.name} - {self.contribution.title}"
        self.assertEqual(str(self.contribution), expected)
        
    def test_mp_relationship(self):
        """Test relationship with MP."""
        self.assertEqual(self.contribution.mp.name, "Test MP")


class MPSerializerTest(TestCase):
    """Test cases for MP serializers."""
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='password123',
            is_staff=True
        )
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a county and subcounty
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
        
        # Create an MP
        self.mp = MP.objects.create(
            name="Test MP",
            subcounty=self.subcounty,
            party="Test Party",
            phone_number="1234567890",
            email="mp@example.com",
            bio="Test bio",
            education="Test education",
            experience="Test experience",
            election_date=timezone.now().date()
        )
        
        # Create an attendance record
        self.attendance = MPAttendance.objects.create(
            mp=self.mp,
            date=timezone.now().date(),
            session_type="Parliament Session",
            status="present",
            notes="Test notes"
        )
        
        # Create a contribution record
        self.contribution = MPContribution.objects.create(
            mp=self.mp,
            date=timezone.now().date(),
            title="Test Contribution",
            description="Test description",
            contribution_type="Bill",
            url="https://example.com/contribution",
            impact_score=8
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
    def test_mp_serialization(self):
        """Test MP serialization."""
        url = reverse('mp-detail', kwargs={'pk': self.mp.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test MP")
        self.assertEqual(response.data['subcounty'], self.subcounty.id)
        self.assertEqual(response.data['party'], "Test Party")
        self.assertEqual(response.data['phone_number'], "1234567890")
        self.assertEqual(response.data['email'], "mp@example.com")
        self.assertEqual(response.data['bio'], "Test bio")
        self.assertEqual(response.data['education'], "Test education")
        self.assertEqual(response.data['experience'], "Test experience")
        
    def test_attendance_serialization(self):
        """Test attendance serialization."""
        url = reverse('mpattendance-detail', kwargs={'pk': self.attendance.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mp'], self.mp.id)
        self.assertEqual(response.data['session_type'], "Parliament Session")
        self.assertEqual(response.data['status'], "present")
        self.assertEqual(response.data['notes'], "Test notes")
        
    def test_contribution_serialization(self):
        """Test contribution serialization."""
        url = reverse('mpcontribution-detail', kwargs={'pk': self.contribution.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mp'], self.mp.id)
        self.assertEqual(response.data['title'], "Test Contribution")
        self.assertEqual(response.data['description'], "Test description")
        self.assertEqual(response.data['contribution_type'], "Bill")
        self.assertEqual(response.data['url'], "https://example.com/contribution")
        self.assertEqual(response.data['impact_score'], 8)


class MPViewSetTest(TestCase):
    """Test cases for MP ViewSet."""
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='password123',
            is_staff=True
        )
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a county and subcounty
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
        
        # Create an MP
        self.mp = MP.objects.create(
            name="Test MP",
            subcounty=self.subcounty,
            party="Test Party",
            phone_number="1234567890",
            email="mp@example.com",
            bio="Test bio",
            education="Test education",
            experience="Test experience",
            election_date=timezone.now().date()
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
    def test_list_mps(self):
        """Test listing MPs."""
        url = reverse('mp-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_mp(self):
        """Test retrieving an MP."""
        url = reverse('mp-detail', kwargs={'pk': self.mp.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test MP")
        
    def test_create_mp(self):
        """Test creating an MP."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('mp-list')
        data = {
            'name': 'New MP',
            'subcounty': self.subcounty.id,
            'party': 'New Party',
            'phone_number': '0987654321',
            'email': 'newmp@example.com',
            'bio': 'New bio',
            'education': 'New education',
            'experience': 'New experience',
            'election_date': timezone.now().date().isoformat()
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MP.objects.count(), 2)
        self.assertEqual(MP.objects.get(name='New MP').party, 'New Party')
        
    def test_update_mp(self):
        """Test updating an MP."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('mp-detail', kwargs={'pk': self.mp.pk})
        data = {
            'bio': 'Updated bio'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mp.refresh_from_db()
        self.assertEqual(self.mp.bio, 'Updated bio')
        
    def test_delete_mp(self):
        """Test deleting an MP."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('mp-detail', kwargs={'pk': self.mp.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MP.objects.count(), 0)
        
    def test_filter_mps_by_county(self):
        """Test filtering MPs by county."""
        # Create another county, subcounty, and MP
        county2 = County.objects.create(
            name="Test County 2",
            code="048",
            governor="Test Governor 2"
        )
        
        subcounty2 = SubCounty.objects.create(
            name="Test SubCounty 2",
            county=county2,
            mp="Test MP 2"
        )
        
        MP.objects.create(
            name="Test MP 2",
            subcounty=subcounty2,
            party="Test Party 2",
            phone_number="9876543210",
            email="mp2@example.com",
            bio="Test bio 2",
            education="Test education 2",
            experience="Test experience 2",
            election_date=timezone.now().date()
        )
        
        url = reverse('mp-list') + f'?county={self.county.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test MP")
        
    def test_filter_mps_by_party(self):
        """Test filtering MPs by party."""
        # Create another MP with a different party
        MP.objects.create(
            name="Test MP 2",
            subcounty=self.subcounty,
            party="Different Party",
            phone_number="9876543210",
            email="mp2@example.com",
            bio="Test bio 2",
            education="Test education 2",
            experience="Test experience 2",
            election_date=timezone.now().date()
        )
        
        url = reverse('mp-list') + '?party=Test%20Party'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test MP")
        
    def test_unauthorized_create(self):
        """Test that regular users cannot create MPs."""
        url = reverse('mp-list')
        data = {
            'name': 'Unauthorized MP',
            'subcounty': self.subcounty.id,
            'party': 'Unauthorized Party',
            'phone_number': '1122334455',
            'email': 'unauthorizedmp@example.com',
            'bio': 'Unauthorized bio',
            'education': 'Unauthorized education',
            'experience': 'Unauthorized experience',
            'election_date': timezone.now().date().isoformat()
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(MP.objects.count(), 1)  # Still just one MP


class MPAttendanceViewSetTest(TestCase):
    """Test cases for MPAttendance ViewSet."""
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='password123',
            is_staff=True
        )
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a county and subcounty
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
        
        # Create an MP
        self.mp = MP.objects.create(
            name="Test MP",
            subcounty=self.subcounty,
            party="Test Party",
            phone_number="1234567890",
            email="mp@example.com",
            bio="Test bio",
            education="Test education",
            experience="Test experience",
            election_date=timezone.now().date()
        )
        
        # Create an attendance record
        self.attendance = MPAttendance.objects.create(
            mp=self.mp,
            date=timezone.now().date(),
            session_type="Parliament Session",
            status="present",
            notes="Test notes"
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
    def test_list_attendances(self):
        """Test listing attendance records."""
        url = reverse('mpattendance-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_attendance(self):
        """Test retrieving an attendance record."""
        url = reverse('mpattendance-detail', kwargs={'pk': self.attendance.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mp'], self.mp.id)
        self.assertEqual(response.data['session_type'], "Parliament Session")
        self.assertEqual(response.data['status'], "present")
        
    def test_create_attendance(self):
        """Test creating an attendance record."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('mpattendance-list')
        today = timezone.now().date()
        data = {
            'mp': self.mp.id,
            'date': today.isoformat(),
            'session_type': 'Committee Meeting',
            'status': 'absent',
            'notes': 'Absent notes'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MPAttendance.objects.count(), 2)
        self.assertEqual(MPAttendance.objects.get(session_type='Committee Meeting').status, 'absent')
        
    def test_update_attendance(self):
        """Test updating an attendance record."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('mpattendance-detail', kwargs={'pk': self.attendance.pk})
        data = {
            'status': 'late',
            'notes': 'Updated notes'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.attendance.refresh_from_db()
        self.assertEqual(self.attendance.status, 'late')
        self.assertEqual(self.attendance.notes, 'Updated notes')
        
    def test_filter_attendance_by_mp(self):
        """Test filtering attendance records by MP."""
        # Create another MP and attendance record
        mp2 = MP.objects.create(
            name="Another MP",
            subcounty=self.subcounty,
            party="Another Party",
            phone_number="9876543210",
            email="another@example.com",
            bio="Another bio",
            education="Another education",
            experience="Another experience",
            election_date=timezone.now().date()
        )
        
        MPAttendance.objects.create(
            mp=mp2,
            date=timezone.now().date(),
            session_type="Committee Meeting",
            status="absent",
            notes="Another notes"
        )
        
        url = reverse('mpattendance-list') + f'?mp={self.mp.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['session_type'], "Parliament Session")
        
    def test_filter_attendance_by_status(self):
        """Test filtering attendance records by status."""
        # Create another attendance record with different status
        MPAttendance.objects.create(
            mp=self.mp,
            date=timezone.now().date() - datetime.timedelta(days=1),
            session_type="Committee Meeting",
            status="absent",
            notes="Absent notes"
        )
        
        url = reverse('mpattendance-list') + '?status=present'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['session_type'], "Parliament Session")


class MPContributionViewSetTest(TestCase):
    """Test cases for MPContribution ViewSet."""
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='password123',
            is_staff=True
        )
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a county and subcounty
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
        
        # Create an MP
        self.mp = MP.objects.create(
            name="Test MP",
            subcounty=self.subcounty,
            party="Test Party",
            phone_number="1234567890",
            email="mp@example.com",
            bio="Test bio",
            education="Test education",
            experience="Test experience",
            election_date=timezone.now().date()
        )
        
        # Create a contribution record
        self.contribution = MPContribution.objects.create(
            mp=self.mp,
            date=timezone.now().date(),
            title="Test Contribution",
            description="Test description",
            contribution_type="Bill",
            url="https://example.com/contribution",
            impact_score=8
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
    def test_list_contributions(self):
        """Test listing contribution records."""
        url = reverse('mpcontribution-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_contribution(self):
        """Test retrieving a contribution record."""
        url = reverse('mpcontribution-detail', kwargs={'pk': self.contribution.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mp'], self.mp.id)
        self.assertEqual(response.data['title'], "Test Contribution")
        
    def test_create_contribution(self):
        """Test creating a contribution record."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('mpcontribution-list')
        today = timezone.now().date()
        data = {
            'mp': self.mp.id,
            'date': today.isoformat(),
            'title': 'New Contribution',
            'description': 'New description',
            'contribution_type': 'Motion',
            'url': 'https://example.com/new',
            'impact_score': 6
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MPContribution.objects.count(), 2)
        self.assertEqual(MPContribution.objects.get(title='New Contribution').contribution_type, 'Motion')
        
    def test_update_contribution(self):
        """Test updating a contribution record."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('mpcontribution-detail', kwargs={'pk': self.contribution.pk})
        data = {
            'title': 'Updated Contribution',
            'impact_score': 9
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.contribution.refresh_from_db()
        self.assertEqual(self.contribution.title, 'Updated Contribution')
        self.assertEqual(self.contribution.impact_score, 9)
        
    def test_filter_contribution_by_mp(self):
        """Test filtering contribution records by MP."""
        # Create another MP and contribution record
        mp2 = MP.objects.create(
            name="Another MP",
            subcounty=self.subcounty,
            party="Another Party",
            phone_number="9876543210",
            email="another@example.com",
            bio="Another bio",
            education="Another education",
            experience="Another experience",
            election_date=timezone.now().date()
        )
        
        MPContribution.objects.create(
            mp=mp2,
            date=timezone.now().date(),
            title="Another Contribution",
            description="Another description",
            contribution_type="Motion",
            url="https://example.com/another",
            impact_score=7
        )
        
        url = reverse('mpcontribution-list') + f'?mp={self.mp.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Test Contribution")
        
    def test_filter_contribution_by_type(self):
        """Test filtering contribution records by type."""
        # Create another contribution record with different type
        MPContribution.objects.create(
            mp=self.mp,
            date=timezone.now().date() - datetime.timedelta(days=1),
            title="Motion Contribution",
            description="Motion description",
            contribution_type="Motion",
            url="https://example.com/motion",
            impact_score=7
        )
        
        url = reverse('mpcontribution-list') + '?contribution_type=Bill'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Test Contribution") 