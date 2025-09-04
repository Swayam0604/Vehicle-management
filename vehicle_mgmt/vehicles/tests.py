from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Vehicle
from .forms import VehicleForm
from users.models import CustomUser

User = get_user_model()

class VehicleModelTest(TestCase):
    """Test Vehicle model using OOP concepts"""
    
    def test_vehicle_creation(self):
        """Test vehicle creation with all fields"""
        vehicle = Vehicle.objects.create(
            vehicle_number='TEST123',
            vehicle_type='Four',
            vehicle_model='Test Model',
            vehicle_description='Test Description'
        )
        
        self.assertEqual(vehicle.vehicle_number, 'TEST123')
        self.assertEqual(vehicle.vehicle_type, 'Four')
        self.assertEqual(vehicle.vehicle_model, 'Test Model')
        self.assertIsNotNone(vehicle.created_at)
        self.assertIsNotNone(vehicle.updated_at)

    def test_vehicle_string_representation(self):
        """Test __str__ method of Vehicle model"""
        vehicle = Vehicle.objects.create(
            vehicle_number='STR123',
            vehicle_type='Two',
            vehicle_model='String Test',
            vehicle_description='String test description'
        )
        
        # Fixed: Your model returns f"{vehicle_number} - {vehicle_model}"
        expected = f"{vehicle.vehicle_number} - {vehicle.vehicle_model}"
        self.assertEqual(str(vehicle), expected)

    def test_vehicle_type_choices(self):
        """Test vehicle type choices validation"""
        valid_types = ['Two', 'Three', 'Four']
        
        for vehicle_type in valid_types:
            vehicle = Vehicle.objects.create(
                vehicle_number=f'TYPE{vehicle_type}',
                vehicle_type=vehicle_type,
                vehicle_model=f'{vehicle_type} Wheeler Test',
                vehicle_description='Type test'
            )
            self.assertEqual(vehicle.vehicle_type, vehicle_type)

    def test_vehicle_unique_number_constraint(self):
        """Test that vehicle numbers must be unique"""
        Vehicle.objects.create(
            vehicle_number='UNIQUE123',
            vehicle_type='Four',
            vehicle_model='First Vehicle',
            vehicle_description='First description'
        )
        
        # Attempting to create another vehicle with same number should fail
        with self.assertRaises(Exception):
            Vehicle.objects.create(
                vehicle_number='UNIQUE123',  # Same number
                vehicle_type='Two',
                vehicle_model='Second Vehicle',
                vehicle_description='Second description'
            )

class VehiclePermissionTest(TestCase):
    """Test role-based access to vehicle operations"""
    
    def setUp(self):
        """Set up users and test vehicle"""
        self.client = Client()
        
        # Create users with different roles
        self.superadmin = CustomUser.objects.create_user(
            username='vehicle_superadmin',
            email='vsuperadmin@test.com',
            password='testpass123',
            role='superadmin',
            is_active=True
        )
        
        self.admin = CustomUser.objects.create_user(
            username='vehicle_admin',
            email='vadmin@test.com',
            password='testpass123',
            role='admin',
            is_active=True
        )
        
        self.user = CustomUser.objects.create_user(
            username='vehicle_user',
            email='vuser@test.com',
            password='testpass123',
            role='user',
            is_active=True
        )
        
        # Create test vehicle
        self.vehicle = Vehicle.objects.create(
            vehicle_number='PERM123',
            vehicle_type='Four',
            vehicle_model='Permission Test',
            vehicle_description='Test permissions'
        )

    def test_vehicle_create_superadmin_only(self):
        """Test only superadmin can create vehicles"""
        # Test superadmin can access create
        self.client.force_login(self.superadmin)
        response = self.client.get(reverse('vehicle_add'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        
        # Test admin gets redirected (using RoleRequiredMixin)
        self.client.force_login(self.admin)
        response = self.client.get(reverse('vehicle_add'))
        self.assertRedirects(response, reverse('vehicle_list'))
        self.client.logout()
        
        # Test user gets redirected
        self.client.force_login(self.user)
        response = self.client.get(reverse('vehicle_add'))
        self.assertRedirects(response, reverse('vehicle_list'))

    def test_vehicle_edit_superadmin_admin(self):
        """Test superadmin and admin can edit vehicles"""
        # Test superadmin can edit
        self.client.force_login(self.superadmin)
        response = self.client.get(reverse('vehicle_edit', kwargs={'pk': self.vehicle.pk}))
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        
        # Test admin can edit
        self.client.force_login(self.admin)
        response = self.client.get(reverse('vehicle_edit', kwargs={'pk': self.vehicle.pk}))
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        
        # Test user cannot edit
        self.client.force_login(self.user)
        response = self.client.get(reverse('vehicle_edit', kwargs={'pk': self.vehicle.pk}))
        self.assertRedirects(response, reverse('vehicle_list'))

    def test_vehicle_delete_superadmin_only(self):
        """Test only superadmin can delete vehicles"""
        # Test superadmin can delete
        self.client.force_login(self.superadmin)
        response = self.client.get(reverse('vehicle_delete', kwargs={'pk': self.vehicle.pk}))
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        
        # Test admin cannot delete
        self.client.force_login(self.admin)
        response = self.client.get(reverse('vehicle_delete', kwargs={'pk': self.vehicle.pk}))
        self.assertRedirects(response, reverse('vehicle_list'))
        
        # Test user cannot delete
        self.client.force_login(self.user)
        response = self.client.get(reverse('vehicle_delete', kwargs={'pk': self.vehicle.pk}))
        self.assertRedirects(response, reverse('vehicle_list'))

    def test_vehicle_list_all_roles(self):
        """Test all roles can view vehicle list"""
        users = [self.superadmin, self.admin, self.user]
        
        for user in users:
            self.client.force_login(user)
            response = self.client.get(reverse('vehicle_list'))
            self.assertEqual(response.status_code, 200)
            self.assertIn('vehicles', response.context)
            self.client.logout()

    def test_vehicle_detail_all_roles(self):
        """Test all roles can view vehicle details"""
        users = [self.superadmin, self.admin, self.user]
        
        for user in users:
            self.client.force_login(user)
            response = self.client.get(reverse('vehicle_detail', kwargs={'pk': self.vehicle.pk}))
            self.assertEqual(response.status_code, 200)
            self.client.logout()

class VehicleCRUDTest(TestCase):
    """Test CRUD operations functionality"""
    
    def setUp(self):
        """Set up superadmin user for CRUD operations"""
        self.client = Client()
        self.superadmin = CustomUser.objects.create_user(
            username='crud_superadmin',
            email='crud@test.com',
            password='testpass123',
            role='superadmin',
            is_active=True
        )
        
        self.admin = CustomUser.objects.create_user(
            username='crud_admin',
            email='crudadmin@test.com',
            password='testpass123',
            role='admin',
            is_active=True
        )

    def test_vehicle_create_operation(self):
        """Test vehicle creation by superadmin"""
        self.client.force_login(self.superadmin)
        
        data = {
            'vehicle_number': 'CRUD123',
            'vehicle_type': 'Two',
            'vehicle_model': 'CRUD Test Model',
            'vehicle_description': 'CRUD test description'
        }
        
        response = self.client.post(reverse('vehicle_add'), data)
        self.assertRedirects(response, reverse('vehicle_list'))
        
        # Verify vehicle was created
        vehicle = Vehicle.objects.get(vehicle_number='CRUD123')
        self.assertEqual(vehicle.vehicle_type, 'Two')
        self.assertEqual(vehicle.vehicle_model, 'CRUD Test Model')

    def test_vehicle_update_operation_by_admin(self):
        """Test vehicle update by admin"""
        vehicle = Vehicle.objects.create(
            vehicle_number='UPD123',
            vehicle_type='Four',
            vehicle_model='Original Model',
            vehicle_description='Original Description'
        )
        
        self.client.force_login(self.admin)  # Admin can edit
        
        data = {
            'vehicle_number': 'UPD123',
            'vehicle_type': 'Four',
            'vehicle_model': 'Updated Model',
            'vehicle_description': 'Updated Description'
        }
        
        response = self.client.post(reverse('vehicle_edit', kwargs={'pk': vehicle.pk}), data)
        self.assertRedirects(response, reverse('vehicle_list'))
        
        # Verify vehicle was updated
        vehicle.refresh_from_db()
        self.assertEqual(vehicle.vehicle_model, 'Updated Model')
        self.assertEqual(vehicle.vehicle_description, 'Updated Description')

    def test_vehicle_delete_operation(self):
        """Test vehicle deletion by superadmin"""
        vehicle = Vehicle.objects.create(
            vehicle_number='DEL123',
            vehicle_type='Three',
            vehicle_model='To Delete',
            vehicle_description='Will be deleted'
        )
        
        self.client.force_login(self.superadmin)
        response = self.client.post(reverse('vehicle_delete', kwargs={'pk': vehicle.pk}))
        self.assertRedirects(response, reverse('vehicle_list'))
        
        # Verify vehicle was deleted
        self.assertFalse(Vehicle.objects.filter(pk=vehicle.pk).exists())

class VehicleFormTest(TestCase):
    """Test vehicle forms using OOP"""
    
    def test_valid_vehicle_form(self):
        """Test valid vehicle form submission"""
        form_data = {
            'vehicle_number': 'FORM123',
            'vehicle_type': 'Four',
            'vehicle_model': 'Form Test Model',
            'vehicle_description': 'Form test description'
        }
        form = VehicleForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_vehicle_form_missing_required_fields(self):
        """Test invalid vehicle form with missing fields"""
        form_data = {
            'vehicle_number': '',  # Required field missing
            'vehicle_type': 'Four',
            'vehicle_model': '',  # Required field missing
            'vehicle_description': 'Test Description'
        }
        form = VehicleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('vehicle_number', form.errors)
        self.assertIn('vehicle_model', form.errors)

    def test_vehicle_form_field_inclusion(self):
        """Test that form includes all required fields"""
        form = VehicleForm()
        expected_fields = ['vehicle_number', 'vehicle_type', 'vehicle_model', 'vehicle_description']
        
        for field in expected_fields:
            self.assertIn(field, form.fields)

class VehicleListFunctionalityTest(TestCase):
    """Test vehicle list view functionality"""
    
    def setUp(self):
        """Set up test data for list functionality"""
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='list_test_user',
            email='listuser@test.com',
            password='testpass123',
            role='user',
            is_active=True
        )
        self.client.force_login(self.user)
        
        # Create vehicles of different types for counting
        Vehicle.objects.create(vehicle_number='TWO1', vehicle_type='Two', vehicle_model='Bike1', vehicle_description='Desc1')
        Vehicle.objects.create(vehicle_number='TWO2', vehicle_type='Two', vehicle_model='Bike2', vehicle_description='Desc2')
        Vehicle.objects.create(vehicle_number='THREE1', vehicle_type='Three', vehicle_model='Auto1', vehicle_description='Desc3')
        Vehicle.objects.create(vehicle_number='FOUR1', vehicle_type='Four', vehicle_model='Car1', vehicle_description='Desc4')
        Vehicle.objects.create(vehicle_number='FOUR2', vehicle_type='Four', vehicle_model='Car2', vehicle_description='Desc5')

    def test_vehicle_list_counts(self):
        """Test that vehicle list shows correct counts by type"""
        response = self.client.get(reverse('vehicle_list'))
        
        self.assertEqual(response.status_code, 200)
        
        # Check context variables match your view logic
        self.assertEqual(response.context['two_wheeler_count'], 2)
        self.assertEqual(response.context['three_wheeler_count'], 1)
        self.assertEqual(response.context['four_wheeler_count'], 2)
        self.assertEqual(len(response.context['vehicles']), 5)  # Total vehicles
