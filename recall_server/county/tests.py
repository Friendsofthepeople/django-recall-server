"""
Tests for the various modules for the `county` Django app.

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

from recall_server.county.models import County, SubCounty, Ward


class CountyModelTest(TestCase):
    """Test cases for the County model."""
    
    def setUp(self):
        """Set up test data."""
        self.county = County.objects.create(
            name="Test County",
            code="047",
            governor="Test Governor"
        )
        
    def test_county_creation(self):
        """Test creating a county object."""
        self.assertEqual(self.county.name, "Test County")
        self.assertEqual(self.county.code, "047")
        self.assertEqual(self.county.governor, "Test Governor")
        
    def test_string_representation(self):
        """Test string representation of a county."""
        self.assertEqual(str(self.county), "Test County")


class SubCountyModelTest(TestCase):
    """Test cases for the SubCounty model."""
    
    def setUp(self):
        """Set up test data."""
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
        
    def test_subcounty_creation(self):
        """Test creating a subcounty object."""
        self.assertEqual(self.subcounty.name, "Test SubCounty")
        self.assertEqual(self.subcounty.county, self.county)
        self.assertEqual(self.subcounty.mp, "Test MP")
        
    def test_string_representation(self):
        """Test string representation of a subcounty."""
        self.assertEqual(str(self.subcounty), "Test SubCounty")
        
    def test_county_relationship(self):
        """Test relationship with county."""
        self.assertEqual(self.subcounty.county.name, "Test County")
        
        # Test reverse relationship
        subcounties = self.county.subcounties.all()
        self.assertEqual(subcounties.count(), 1)
        self.assertEqual(subcounties.first().name, "Test SubCounty")


class WardModelTest(TestCase):
    """Test cases for the Ward model."""
    
    def setUp(self):
        """Set up test data."""
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
        
    def test_ward_creation(self):
        """Test creating a ward object."""
        self.assertEqual(self.ward.name, "Test Ward")
        self.assertEqual(self.ward.subcounty, self.subcounty)
        self.assertEqual(self.ward.mca, "Test MCA")
        
    def test_string_representation(self):
        """Test string representation of a ward."""
        self.assertEqual(str(self.ward), "Test Ward")
        
    def test_subcounty_relationship(self):
        """Test relationship with subcounty."""
        self.assertEqual(self.ward.subcounty.name, "Test SubCounty")
        
        # Test reverse relationship
        wards = self.subcounty.wards.all()
        self.assertEqual(wards.count(), 1)
        self.assertEqual(wards.first().name, "Test Ward")
        
    def test_county_access(self):
        """Test accessing county through ward."""
        self.assertEqual(self.ward.subcounty.county.name, "Test County")


class CountySerializerTest(TestCase):
    """Test cases for County serializers."""
    
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
        
    def test_county_serialization(self):
        """Test county serialization."""
        self.client.force_authenticate(user=self.user)
        url = reverse('county-detail', kwargs={'pk': self.county.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test County")
        self.assertEqual(response.data['code'], "047")
        self.assertEqual(response.data['governor'], "Test Governor")
        
    def test_subcounty_serialization(self):
        """Test subcounty serialization."""
        self.client.force_authenticate(user=self.user)
        url = reverse('subcounty-detail', kwargs={'pk': self.subcounty.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test SubCounty")
        self.assertEqual(response.data['mp'], "Test MP")
        self.assertEqual(response.data['county'], self.county.id)
        
    def test_ward_serialization(self):
        """Test ward serialization."""
        self.client.force_authenticate(user=self.user)
        url = reverse('ward-detail', kwargs={'pk': self.ward.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Ward")
        self.assertEqual(response.data['mca'], "Test MCA")
        self.assertEqual(response.data['subcounty'], self.subcounty.id)


class CountyViewSetTest(TestCase):
    """Test cases for County ViewSet."""
    
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
        self.county = County.objects.create(
            name="Test County",
            code="047",
            governor="Test Governor"
        )
        
    def test_list_counties(self):
        """Test listing counties."""
        self.client.force_authenticate(user=self.user)
        url = reverse('county-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_county(self):
        """Test retrieving a county."""
        self.client.force_authenticate(user=self.user)
        url = reverse('county-detail', kwargs={'pk': self.county.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test County")
        
    def test_create_county(self):
        """Test creating a county."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('county-list')
        data = {
            'name': 'New County',
            'code': '048',
            'governor': 'New Governor'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(County.objects.count(), 2)
        self.assertEqual(County.objects.get(name='New County').governor, 'New Governor')
        
    def test_update_county(self):
        """Test updating a county."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('county-detail', kwargs={'pk': self.county.pk})
        data = {
            'governor': 'Updated Governor'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.county.refresh_from_db()
        self.assertEqual(self.county.governor, 'Updated Governor')
        
    def test_delete_county(self):
        """Test deleting a county."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('county-detail', kwargs={'pk': self.county.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(County.objects.count(), 0)
        
    def test_unauthorized_create(self):
        """Test that regular users cannot create counties."""
        self.client.force_authenticate(user=self.user)
        url = reverse('county-list')
        data = {
            'name': 'Unauthorized County',
            'code': '049',
            'governor': 'Unauthorized Governor'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(County.objects.count(), 1)  # Still just one county
        
    def test_unauthorized_update(self):
        """Test that regular users cannot update counties."""
        self.client.force_authenticate(user=self.user)
        url = reverse('county-detail', kwargs={'pk': self.county.pk})
        data = {
            'governor': 'Unauthorized Update'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.county.refresh_from_db()
        self.assertEqual(self.county.governor, 'Test Governor')  # Unchanged
        
    def test_unauthorized_delete(self):
        """Test that regular users cannot delete counties."""
        self.client.force_authenticate(user=self.user)
        url = reverse('county-detail', kwargs={'pk': self.county.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(County.objects.count(), 1)  # Still exists


class SubCountyViewSetTest(TestCase):
    """Test cases for SubCounty ViewSet."""
    
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
        
    def test_list_subcounties(self):
        """Test listing subcounties."""
        self.client.force_authenticate(user=self.user)
        url = reverse('subcounty-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_filter_subcounties_by_county(self):
        """Test filtering subcounties by county."""
        self.client.force_authenticate(user=self.user)
        url = reverse('subcounty-list') + f'?county={self.county.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test SubCounty")
        
    def test_create_subcounty(self):
        """Test creating a subcounty."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('subcounty-list')
        data = {
            'name': 'New SubCounty',
            'county': self.county.id,
            'mp': 'New MP'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SubCounty.objects.count(), 2)
        self.assertEqual(SubCounty.objects.get(name='New SubCounty').mp, 'New MP')


class WardViewSetTest(TestCase):
    """Test cases for Ward ViewSet."""
    
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
        
    def test_list_wards(self):
        """Test listing wards."""
        self.client.force_authenticate(user=self.user)
        url = reverse('ward-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_filter_wards_by_subcounty(self):
        """Test filtering wards by subcounty."""
        self.client.force_authenticate(user=self.user)
        url = reverse('ward-list') + f'?subcounty={self.subcounty.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Ward")
        
    def test_create_ward(self):
        """Test creating a ward."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('ward-list')
        data = {
            'name': 'New Ward',
            'subcounty': self.subcounty.id,
            'mca': 'New MCA'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ward.objects.count(), 2)
        self.assertEqual(Ward.objects.get(name='New Ward').mca, 'New MCA')
