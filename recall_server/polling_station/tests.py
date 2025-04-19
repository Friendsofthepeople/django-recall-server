from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
import datetime

from recall_server.polling_station.models import PollingStation, PollingOfficer, ElectionResults
from recall_server.county.models import County, SubCounty, Ward


class PollingStationModelTest(TestCase):
    """Test cases for the PollingStation model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a county, subcounty, and ward
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
        
        # Create a polling station
        self.polling_station = PollingStation.objects.create(
            name="Test Polling Station",
            code="PS001",
            ward=self.ward,
            location_description="Test location",
            registered_voters=1000,
            longitude=36.8219,
            latitude=-1.2921,
            status="active"
        )
        
    def test_polling_station_creation(self):
        """Test creating a polling station object."""
        self.assertEqual(self.polling_station.name, "Test Polling Station")
        self.assertEqual(self.polling_station.code, "PS001")
        self.assertEqual(self.polling_station.ward, self.ward)
        self.assertEqual(self.polling_station.location_description, "Test location")
        self.assertEqual(self.polling_station.registered_voters, 1000)
        self.assertEqual(self.polling_station.longitude, 36.8219)
        self.assertEqual(self.polling_station.latitude, -1.2921)
        self.assertEqual(self.polling_station.status, "active")
        
    def test_string_representation(self):
        """Test string representation of a polling station."""
        self.assertEqual(str(self.polling_station), "Test Polling Station (PS001)")
        
    def test_ward_relationship(self):
        """Test relationship with ward."""
        self.assertEqual(self.polling_station.ward.name, "Test Ward")
        
    def test_subcounty_access(self):
        """Test accessing subcounty through ward."""
        self.assertEqual(self.polling_station.ward.subcounty.name, "Test SubCounty")
        
    def test_county_access(self):
        """Test accessing county through ward.subcounty."""
        self.assertEqual(self.polling_station.ward.subcounty.county.name, "Test County")


class PollingOfficerModelTest(TestCase):
    """Test cases for the PollingOfficer model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a county, subcounty, and ward
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
        
        # Create a polling station
        self.polling_station = PollingStation.objects.create(
            name="Test Polling Station",
            code="PS001",
            ward=self.ward,
            location_description="Test location",
            registered_voters=1000,
            longitude=36.8219,
            latitude=-1.2921,
            status="active"
        )
        
        # Create a polling officer
        self.officer = PollingOfficer.objects.create(
            user=self.user,
            id_number="12345678",
            phone_number="1234567890",
            position="Presiding Officer",
            polling_station=self.polling_station,
            status="active"
        )
        
    def test_officer_creation(self):
        """Test creating a polling officer."""
        self.assertEqual(self.officer.user, self.user)
        self.assertEqual(self.officer.id_number, "12345678")
        self.assertEqual(self.officer.phone_number, "1234567890")
        self.assertEqual(self.officer.position, "Presiding Officer")
        self.assertEqual(self.officer.polling_station, self.polling_station)
        self.assertEqual(self.officer.status, "active")
        
    def test_string_representation(self):
        """Test string representation of a polling officer."""
        expected = f"{self.user.username} - {self.polling_station.name}"
        self.assertEqual(str(self.officer), expected)
        
    def test_user_relationship(self):
        """Test relationship with user."""
        self.assertEqual(self.officer.user.username, "testuser")
        
    def test_polling_station_relationship(self):
        """Test relationship with polling station."""
        self.assertEqual(self.officer.polling_station.name, "Test Polling Station")


class ElectionResultsModelTest(TestCase):
    """Test cases for the ElectionResults model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a county, subcounty, and ward
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
        
        # Create a polling station
        self.polling_station = PollingStation.objects.create(
            name="Test Polling Station",
            code="PS001",
            ward=self.ward,
            location_description="Test location",
            registered_voters=1000,
            longitude=36.8219,
            latitude=-1.2921,
            status="active"
        )
        
        # Create election results
        self.results = ElectionResults.objects.create(
            polling_station=self.polling_station,
            election_date=timezone.now().date(),
            election_type="General",
            position="President",
            candidate_name="Test Candidate",
            party="Test Party",
            votes=500,
            is_verified=True,
            verification_timestamp=timezone.now()
        )
        
    def test_results_creation(self):
        """Test creating election results."""
        self.assertEqual(self.results.polling_station, self.polling_station)
        self.assertIsNotNone(self.results.election_date)
        self.assertEqual(self.results.election_type, "General")
        self.assertEqual(self.results.position, "President")
        self.assertEqual(self.results.candidate_name, "Test Candidate")
        self.assertEqual(self.results.party, "Test Party")
        self.assertEqual(self.results.votes, 500)
        self.assertTrue(self.results.is_verified)
        self.assertIsNotNone(self.results.verification_timestamp)
        
    def test_string_representation(self):
        """Test string representation of election results."""
        expected = f"{self.polling_station.name} - {self.results.position} - {self.results.candidate_name}: {self.results.votes}"
        self.assertEqual(str(self.results), expected)
        
    def test_polling_station_relationship(self):
        """Test relationship with polling station."""
        self.assertEqual(self.results.polling_station.name, "Test Polling Station")


class PollingStationSerializerTest(TestCase):
    """Test cases for polling station serializers."""
    
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
        
        # Create a county, subcounty, and ward
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
        
        # Create a polling station
        self.polling_station = PollingStation.objects.create(
            name="Test Polling Station",
            code="PS001",
            ward=self.ward,
            location_description="Test location",
            registered_voters=1000,
            longitude=36.8219,
            latitude=-1.2921,
            status="active"
        )
        
        # Create a polling officer
        self.officer = PollingOfficer.objects.create(
            user=self.user,
            id_number="12345678",
            phone_number="1234567890",
            position="Presiding Officer",
            polling_station=self.polling_station,
            status="active"
        )
        
        # Create election results
        self.results = ElectionResults.objects.create(
            polling_station=self.polling_station,
            election_date=timezone.now().date(),
            election_type="General",
            position="President",
            candidate_name="Test Candidate",
            party="Test Party",
            votes=500,
            is_verified=True,
            verification_timestamp=timezone.now()
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
    def test_polling_station_serialization(self):
        """Test polling station serialization."""
        url = reverse('pollingstation-detail', kwargs={'pk': self.polling_station.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Polling Station")
        self.assertEqual(response.data['code'], "PS001")
        self.assertEqual(response.data['ward'], self.ward.id)
        self.assertEqual(response.data['location_description'], "Test location")
        self.assertEqual(response.data['registered_voters'], 1000)
        self.assertEqual(response.data['longitude'], 36.8219)
        self.assertEqual(response.data['latitude'], -1.2921)
        self.assertEqual(response.data['status'], "active")
        
    def test_polling_officer_serialization(self):
        """Test polling officer serialization."""
        url = reverse('pollingofficer-detail', kwargs={'pk': self.officer.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['id_number'], "12345678")
        self.assertEqual(response.data['phone_number'], "1234567890")
        self.assertEqual(response.data['position'], "Presiding Officer")
        self.assertEqual(response.data['polling_station'], self.polling_station.id)
        self.assertEqual(response.data['status'], "active")
        
    def test_election_results_serialization(self):
        """Test election results serialization."""
        url = reverse('electionresults-detail', kwargs={'pk': self.results.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['polling_station'], self.polling_station.id)
        self.assertEqual(response.data['election_type'], "General")
        self.assertEqual(response.data['position'], "President")
        self.assertEqual(response.data['candidate_name'], "Test Candidate")
        self.assertEqual(response.data['party'], "Test Party")
        self.assertEqual(response.data['votes'], 500)
        self.assertEqual(response.data['is_verified'], True)


class PollingStationViewSetTest(TestCase):
    """Test cases for PollingStation ViewSet."""
    
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
        
        # Create a county, subcounty, and ward
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
        
        # Create a polling station
        self.polling_station = PollingStation.objects.create(
            name="Test Polling Station",
            code="PS001",
            ward=self.ward,
            location_description="Test location",
            registered_voters=1000,
            longitude=36.8219,
            latitude=-1.2921,
            status="active"
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
    def test_list_polling_stations(self):
        """Test listing polling stations."""
        url = reverse('pollingstation-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_polling_station(self):
        """Test retrieving a polling station."""
        url = reverse('pollingstation-detail', kwargs={'pk': self.polling_station.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Polling Station")
        
    def test_create_polling_station(self):
        """Test creating a polling station."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('pollingstation-list')
        data = {
            'name': 'New Polling Station',
            'code': 'PS002',
            'ward': self.ward.id,
            'location_description': 'New location',
            'registered_voters': 1500,
            'longitude': 36.8220,
            'latitude': -1.2922,
            'status': 'active'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PollingStation.objects.count(), 2)
        self.assertEqual(PollingStation.objects.get(code='PS002').name, 'New Polling Station')
        
    def test_update_polling_station(self):
        """Test updating a polling station."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('pollingstation-detail', kwargs={'pk': self.polling_station.pk})
        data = {
            'registered_voters': 1200,
            'location_description': 'Updated location'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.polling_station.refresh_from_db()
        self.assertEqual(self.polling_station.registered_voters, 1200)
        self.assertEqual(self.polling_station.location_description, 'Updated location')
        
    def test_delete_polling_station(self):
        """Test deleting a polling station."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('pollingstation-detail', kwargs={'pk': self.polling_station.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PollingStation.objects.count(), 0)
        
    def test_filter_polling_stations_by_ward(self):
        """Test filtering polling stations by ward."""
        # Create another ward and polling station
        ward2 = Ward.objects.create(
            name="Another Ward",
            subcounty=self.subcounty,
            mca="Another MCA"
        )
        
        PollingStation.objects.create(
            name="Another Polling Station",
            code="PS002",
            ward=ward2,
            location_description="Another location",
            registered_voters=1500,
            longitude=36.8220,
            latitude=-1.2922,
            status="active"
        )
        
        url = reverse('pollingstation-list') + f'?ward={self.ward.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Polling Station")
        
    def test_filter_polling_stations_by_status(self):
        """Test filtering polling stations by status."""
        # Create another polling station with different status
        PollingStation.objects.create(
            name="Inactive Polling Station",
            code="PS003",
            ward=self.ward,
            location_description="Inactive location",
            registered_voters=800,
            longitude=36.8221,
            latitude=-1.2923,
            status="inactive"
        )
        
        url = reverse('pollingstation-list') + '?status=active'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Polling Station")
        
    def test_unauthorized_create(self):
        """Test that regular users cannot create polling stations."""
        url = reverse('pollingstation-list')
        data = {
            'name': 'Unauthorized Polling Station',
            'code': 'PS999',
            'ward': self.ward.id,
            'location_description': 'Unauthorized location',
            'registered_voters': 999,
            'longitude': 36.8299,
            'latitude': -1.2999,
            'status': 'active'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(PollingStation.objects.count(), 1)  # Still just one polling station


class PollingOfficerViewSetTest(TestCase):
    """Test cases for PollingOfficer ViewSet."""
    
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
        
        # Create another user for officer testing
        self.officer_user = User.objects.create_user(
            username='officeruser',
            email='officer@example.com',
            password='password123'
        )
        
        # Create a county, subcounty, and ward
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
        
        # Create a polling station
        self.polling_station = PollingStation.objects.create(
            name="Test Polling Station",
            code="PS001",
            ward=self.ward,
            location_description="Test location",
            registered_voters=1000,
            longitude=36.8219,
            latitude=-1.2921,
            status="active"
        )
        
        # Create a polling officer
        self.officer = PollingOfficer.objects.create(
            user=self.officer_user,
            id_number="12345678",
            phone_number="1234567890",
            position="Presiding Officer",
            polling_station=self.polling_station,
            status="active"
        )
        
        # Authenticate the client as admin
        self.client.force_authenticate(user=self.admin_user)
        
    def test_list_officers(self):
        """Test listing polling officers."""
        url = reverse('pollingofficer-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_officer(self):
        """Test retrieving a polling officer."""
        url = reverse('pollingofficer-detail', kwargs={'pk': self.officer.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.officer_user.id)
        self.assertEqual(response.data['position'], "Presiding Officer")
        
    def test_create_officer(self):
        """Test creating a polling officer."""
        url = reverse('pollingofficer-list')
        data = {
            'user': self.user.id,
            'id_number': '87654321',
            'phone_number': '0987654321',
            'position': 'Clerk',
            'polling_station': self.polling_station.id,
            'status': 'active'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PollingOfficer.objects.count(), 2)
        self.assertEqual(PollingOfficer.objects.get(id_number='87654321').position, 'Clerk')
        
    def test_update_officer(self):
        """Test updating a polling officer."""
        url = reverse('pollingofficer-detail', kwargs={'pk': self.officer.pk})
        data = {
            'position': 'Deputy Presiding Officer',
            'status': 'inactive'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.officer.refresh_from_db()
        self.assertEqual(self.officer.position, 'Deputy Presiding Officer')
        self.assertEqual(self.officer.status, 'inactive')
        
    def test_filter_officers_by_polling_station(self):
        """Test filtering polling officers by polling station."""
        # Create another polling station and officer
        station2 = PollingStation.objects.create(
            name="Another Polling Station",
            code="PS002",
            ward=self.ward,
            location_description="Another location",
            registered_voters=1500,
            longitude=36.8220,
            latitude=-1.2922,
            status="active"
        )
        
        PollingOfficer.objects.create(
            user=self.user,
            id_number="87654321",
            phone_number="0987654321",
            position="Clerk",
            polling_station=station2,
            status="active"
        )
        
        url = reverse('pollingofficer-list') + f'?polling_station={self.polling_station.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['position'], "Presiding Officer")
        
    def test_filter_officers_by_status(self):
        """Test filtering polling officers by status."""
        # Create another officer with different status
        PollingOfficer.objects.create(
            user=self.user,
            id_number="87654321",
            phone_number="0987654321",
            position="Clerk",
            polling_station=self.polling_station,
            status="inactive"
        )
        
        url = reverse('pollingofficer-list') + '?status=active'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id_number'], "12345678")
        
    def test_unauthorized_access(self):
        """Test unauthorized access to polling officer endpoints."""
        # Authenticate as a regular user
        self.client.force_authenticate(user=self.user)
        
        url = reverse('pollingofficer-list')
        data = {
            'user': self.user.id,
            'id_number': '11111111',
            'phone_number': '1111111111',
            'position': 'Unauthorized Position',
            'polling_station': self.polling_station.id,
            'status': 'active'
        }
        response = self.client.post(url, data)
        
        # Should be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(PollingOfficer.objects.count(), 1)  # Still just one officer


class ElectionResultsViewSetTest(TestCase):
    """Test cases for ElectionResults ViewSet."""
    
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
        
        # Create a county, subcounty, and ward
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
        
        # Create a polling station
        self.polling_station = PollingStation.objects.create(
            name="Test Polling Station",
            code="PS001",
            ward=self.ward,
            location_description="Test location",
            registered_voters=1000,
            longitude=36.8219,
            latitude=-1.2921,
            status="active"
        )
        
        # Create election results
        self.results = ElectionResults.objects.create(
            polling_station=self.polling_station,
            election_date=timezone.now().date(),
            election_type="General",
            position="President",
            candidate_name="Test Candidate",
            party="Test Party",
            votes=500,
            is_verified=True,
            verification_timestamp=timezone.now()
        )
        
        # Create an officer user
        self.officer_user = User.objects.create_user(
            username='officeruser',
            email='officer@example.com',
            password='password123'
        )
        
        # Create polling officer
        self.officer = PollingOfficer.objects.create(
            user=self.officer_user,
            id_number="12345678",
            phone_number="1234567890",
            position="Presiding Officer",
            polling_station=self.polling_station,
            status="active"
        )
        
        # Authenticate the client as a polling officer
        self.client.force_authenticate(user=self.officer_user)
        
    def test_list_results(self):
        """Test listing election results."""
        url = reverse('electionresults-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_results(self):
        """Test retrieving election results."""
        url = reverse('electionresults-detail', kwargs={'pk': self.results.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['polling_station'], self.polling_station.id)
        self.assertEqual(response.data['candidate_name'], "Test Candidate")
        self.assertEqual(response.data['votes'], 500)
        
    def test_create_results(self):
        """Test creating election results."""
        url = reverse('electionresults-list')
        today = timezone.now().date()
        data = {
            'polling_station': self.polling_station.id,
            'election_date': today.isoformat(),
            'election_type': 'General',
            'position': 'Governor',
            'candidate_name': 'Governor Candidate',
            'party': 'Governor Party',
            'votes': 400,
            'is_verified': False
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ElectionResults.objects.count(), 2)
        self.assertEqual(ElectionResults.objects.get(position='Governor').candidate_name, 'Governor Candidate')
        
    def test_update_results(self):
        """Test updating election results."""
        url = reverse('electionresults-detail', kwargs={'pk': self.results.pk})
        data = {
            'votes': 550,
            'is_verified': False
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.results.refresh_from_db()
        self.assertEqual(self.results.votes, 550)
        self.assertFalse(self.results.is_verified)
        
    def test_verify_results(self):
        """Test verifying election results."""
        # Create unverified results
        unverified = ElectionResults.objects.create(
            polling_station=self.polling_station,
            election_date=timezone.now().date(),
            election_type="General",
            position="Governor",
            candidate_name="Governor Candidate",
            party="Governor Party",
            votes=400,
            is_verified=False
        )
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('electionresults-detail', kwargs={'pk': unverified.pk})
        data = {
            'is_verified': True
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        unverified.refresh_from_db()
        self.assertTrue(unverified.is_verified)
        self.assertIsNotNone(unverified.verification_timestamp)
        
    def test_filter_results_by_polling_station(self):
        """Test filtering election results by polling station."""
        # Create another polling station and results
        station2 = PollingStation.objects.create(
            name="Another Polling Station",
            code="PS002",
            ward=self.ward,
            location_description="Another location",
            registered_voters=1500,
            longitude=36.8220,
            latitude=-1.2922,
            status="active"
        )
        
        ElectionResults.objects.create(
            polling_station=station2,
            election_date=timezone.now().date(),
            election_type="General",
            position="President",
            candidate_name="Test Candidate",
            party="Test Party",
            votes=600,
            is_verified=True,
            verification_timestamp=timezone.now()
        )
        
        url = reverse('electionresults-list') + f'?polling_station={self.polling_station.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['votes'], 500)
        
    def test_filter_results_by_position(self):
        """Test filtering election results by position."""
        # Create another result with different position
        ElectionResults.objects.create(
            polling_station=self.polling_station,
            election_date=timezone.now().date(),
            election_type="General",
            position="Governor",
            candidate_name="Governor Candidate",
            party="Governor Party",
            votes=400,
            is_verified=True,
            verification_timestamp=timezone.now()
        )
        
        url = reverse('electionresults-list') + '?position=President'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['candidate_name'], "Test Candidate")
        
    def test_filter_results_by_verification(self):
        """Test filtering election results by verification status."""
        # Create unverified results
        ElectionResults.objects.create(
            polling_station=self.polling_station,
            election_date=timezone.now().date(),
            election_type="General",
            position="Governor",
            candidate_name="Governor Candidate",
            party="Governor Party",
            votes=400,
            is_verified=False
        )
        
        url = reverse('electionresults-list') + '?is_verified=true'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['position'], "President") 