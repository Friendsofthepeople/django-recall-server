"""
Tests for the various modules for the `diaspora` Django app.

Note:
    - Tests should be written using the `unittest` framework test style.
    - Prefer `unittest.TestCase` over `django.test.TestCase` for
      non-DB or transaction independent tests.
    - Consider segregating this test file to target app modules if
      the file grows large (ie. `test_models`, `test_views`, etc).
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from recall_server.diaspora.models import DiasporaRegion, DiasporaVoter


class DiasporaRegionModelTest(TestCase):
    """Test cases for the DiasporaRegion model."""
    
    def setUp(self):
        """Set up test data."""
        self.region = DiasporaRegion.objects.create(
            name="North America",
            country="United States",
            city="New York",
            ambassador="Test Ambassador"
        )
        
    def test_region_creation(self):
        """Test creating a diaspora region object."""
        self.assertEqual(self.region.name, "North America")
        self.assertEqual(self.region.country, "United States")
        self.assertEqual(self.region.city, "New York")
        self.assertEqual(self.region.ambassador, "Test Ambassador")
        
    def test_string_representation(self):
        """Test string representation of a diaspora region."""
        self.assertEqual(str(self.region), "North America - United States, New York")


class DiasporaVoterModelTest(TestCase):
    """Test cases for the DiasporaVoter model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a user
        self.user = User.objects.create_user(
            username='diaspora_user',
            email='diaspora@example.com',
            password='password123'
        )
        
        # Create a diaspora region
        self.region = DiasporaRegion.objects.create(
            name="North America",
            country="United States",
            city="New York",
            ambassador="Test Ambassador"
        )
        
        # Create a diaspora voter
        self.voter = DiasporaVoter.objects.create(
            user=self.user,
            region=self.region,
            passport_number="A12345678",
            country_of_residence="United States",
            occupation="Software Engineer"
        )
        
    def test_voter_creation(self):
        """Test creating a diaspora voter object."""
        self.assertEqual(self.voter.user, self.user)
        self.assertEqual(self.voter.region, self.region)
        self.assertEqual(self.voter.passport_number, "A12345678")
        self.assertEqual(self.voter.country_of_residence, "United States")
        self.assertEqual(self.voter.occupation, "Software Engineer")
        
    def test_string_representation(self):
        """Test string representation of a diaspora voter."""
        self.assertEqual(str(self.voter), "diaspora_user - North America")
        
    def test_user_relationship(self):
        """Test relationship with user."""
        self.assertEqual(self.voter.user.username, "diaspora_user")
        self.assertEqual(self.voter.user.email, "diaspora@example.com")
        
    def test_region_relationship(self):
        """Test relationship with region."""
        self.assertEqual(self.voter.region.name, "North America")
        self.assertEqual(self.voter.region.country, "United States")
        
    def test_unique_user_constraint(self):
        """Test that a user can only have one diaspora voter profile."""
        # Try to create another voter profile for the same user
        with self.assertRaises(Exception):  # Could be IntegrityError or ValidationError
            DiasporaVoter.objects.create(
                user=self.user,
                region=self.region,
                passport_number="B98765432",
                country_of_residence="Canada",
                occupation="Teacher"
            )


class DiasporaRegionSerializerTest(TestCase):
    """Test cases for DiasporaRegion serializer."""
    
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
        
        # Create test data
        self.region = DiasporaRegion.objects.create(
            name="North America",
            country="United States",
            city="New York",
            ambassador="Test Ambassador"
        )
        
    def test_region_serialization(self):
        """Test diaspora region serialization."""
        self.client.force_authenticate(user=self.user)
        url = reverse('diasporaregion-detail', kwargs={'pk': self.region.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "North America")
        self.assertEqual(response.data['country'], "United States")
        self.assertEqual(response.data['city'], "New York")
        self.assertEqual(response.data['ambassador'], "Test Ambassador")


class DiasporaVoterSerializerTest(TestCase):
    """Test cases for DiasporaVoter serializer."""
    
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
        
        # Create test data
        self.region = DiasporaRegion.objects.create(
            name="North America",
            country="United States",
            city="New York",
            ambassador="Test Ambassador"
        )
        
        self.voter = DiasporaVoter.objects.create(
            user=self.user,
            region=self.region,
            passport_number="A12345678",
            country_of_residence="United States",
            occupation="Software Engineer"
        )
        
    def test_voter_serialization(self):
        """Test diaspora voter serialization."""
        self.client.force_authenticate(user=self.user)
        url = reverse('diasporavoter-detail', kwargs={'pk': self.voter.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['region'], self.region.id)
        self.assertEqual(response.data['passport_number'], "A12345678")
        self.assertEqual(response.data['country_of_residence'], "United States")
        self.assertEqual(response.data['occupation'], "Software Engineer")


class DiasporaRegionViewSetTest(TestCase):
    """Test cases for DiasporaRegion ViewSet."""
    
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
        
        # Create test data
        self.region = DiasporaRegion.objects.create(
            name="North America",
            country="United States",
            city="New York",
            ambassador="Test Ambassador"
        )
        
    def test_list_regions(self):
        """Test listing diaspora regions."""
        self.client.force_authenticate(user=self.user)
        url = reverse('diasporaregion-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_region(self):
        """Test retrieving a diaspora region."""
        self.client.force_authenticate(user=self.user)
        url = reverse('diasporaregion-detail', kwargs={'pk': self.region.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "North America")
        
    def test_create_region(self):
        """Test creating a diaspora region."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('diasporaregion-list')
        data = {
            'name': 'Europe',
            'country': 'United Kingdom',
            'city': 'London',
            'ambassador': 'UK Ambassador'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DiasporaRegion.objects.count(), 2)
        self.assertEqual(DiasporaRegion.objects.get(name='Europe').ambassador, 'UK Ambassador')
        
    def test_update_region(self):
        """Test updating a diaspora region."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('diasporaregion-detail', kwargs={'pk': self.region.pk})
        data = {
            'ambassador': 'Updated Ambassador'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.region.refresh_from_db()
        self.assertEqual(self.region.ambassador, 'Updated Ambassador')
        
    def test_delete_region(self):
        """Test deleting a diaspora region."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('diasporaregion-detail', kwargs={'pk': self.region.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DiasporaRegion.objects.count(), 0)
        
    def test_filter_regions_by_country(self):
        """Test filtering diaspora regions by country."""
        # Create another region
        DiasporaRegion.objects.create(
            name="Europe",
            country="United Kingdom",
            city="London",
            ambassador="UK Ambassador"
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('diasporaregion-list') + '?country=United%20States'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "North America")


class DiasporaVoterViewSetTest(TestCase):
    """Test cases for DiasporaVoter ViewSet."""
    
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
        
        # Create another user to test with
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password123'
        )
        
        # Create test data
        self.region = DiasporaRegion.objects.create(
            name="North America",
            country="United States",
            city="New York",
            ambassador="Test Ambassador"
        )
        
        self.voter = DiasporaVoter.objects.create(
            user=self.user,
            region=self.region,
            passport_number="A12345678",
            country_of_residence="United States",
            occupation="Software Engineer"
        )
        
    def test_list_voters(self):
        """Test listing diaspora voters."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('diasporavoter-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_voter(self):
        """Test retrieving a diaspora voter."""
        self.client.force_authenticate(user=self.user)
        url = reverse('diasporavoter-detail', kwargs={'pk': self.voter.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['region'], self.region.id)
        
    def test_create_voter(self):
        """Test creating a diaspora voter."""
        self.client.force_authenticate(user=self.user2)
        url = reverse('diasporavoter-list')
        data = {
            'user': self.user2.id,
            'region': self.region.id,
            'passport_number': 'B98765432',
            'country_of_residence': 'Canada',
            'occupation': 'Teacher'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DiasporaVoter.objects.count(), 2)
        self.assertEqual(DiasporaVoter.objects.get(passport_number='B98765432').occupation, 'Teacher')
        
    def test_update_voter(self):
        """Test updating a diaspora voter."""
        self.client.force_authenticate(user=self.user)
        url = reverse('diasporavoter-detail', kwargs={'pk': self.voter.pk})
        data = {
            'occupation': 'Updated Occupation'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.voter.refresh_from_db()
        self.assertEqual(self.voter.occupation, 'Updated Occupation')
        
    def test_delete_voter(self):
        """Test deleting a diaspora voter."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('diasporavoter-detail', kwargs={'pk': self.voter.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DiasporaVoter.objects.count(), 0)
        
    def test_filter_voters_by_region(self):
        """Test filtering diaspora voters by region."""
        # Create another region and voter
        region2 = DiasporaRegion.objects.create(
            name="Europe",
            country="United Kingdom",
            city="London",
            ambassador="UK Ambassador"
        )
        
        DiasporaVoter.objects.create(
            user=self.user2,
            region=region2,
            passport_number="B98765432",
            country_of_residence="United Kingdom",
            occupation="Teacher"
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('diasporavoter-list') + f'?region={self.region.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['passport_number'], "A12345678")
        
    def test_unauthorized_access(self):
        """Test unauthorized access to diaspora voter endpoints."""
        # Logout
        self.client.force_authenticate(user=None)
        
        # Try to list diaspora voters
        url = reverse('diasporavoter-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Try to create a diaspora voter without authentication
        data = {
            'user': self.user2.id,
            'region': self.region.id,
            'passport_number': 'B98765432',
            'country_of_residence': 'Canada',
            'occupation': 'Teacher'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
