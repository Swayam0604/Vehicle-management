from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from django.contrib.messages import get_messages
from .models import CustomUser
from .forms import CustomUserRegistrationForm, CustomLoginForm
from .views import otp_storage
from django.conf import settings

User = get_user_model()

class CustomUserModelTest(TestCase):
    """Test the CustomUser model using OOP concepts"""
    
    def test_user_creation_with_roles(self):
        """Test user creation with different roles"""
        superadmin = CustomUser.objects.create_user(
            username='test_superadmin',
            email='superadmin@test.com',
            password='testpass123',
            role='superadmin'
        )
        admin = CustomUser.objects.create_user(
            username='test_admin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        user = CustomUser.objects.create_user(
            username='test_user',
            email='user@test.com',
            password='testpass123',
            role='user'
        )
        
        self.assertEqual(superadmin.role, 'superadmin')
        self.assertEqual(admin.role, 'admin')
        self.assertEqual(user.role, 'user')
        
        # Test that all users are created properly
        self.assertTrue(isinstance(superadmin, CustomUser))
        self.assertTrue(isinstance(admin, CustomUser))
        self.assertTrue(isinstance(user, CustomUser))

    def test_user_string_representation(self):
        """Test the string representation of user"""
        test_user = CustomUser.objects.create_user(
            username='string_test_user',
            email='stringtest@test.com',
            password='testpass123',
            role='admin'
        )
        
        expected = f"{test_user.username} ({test_user.role})"
        self.assertEqual(str(test_user), expected)

    def test_default_user_role(self):
        """Test default role assignment"""
        default_user = CustomUser.objects.create_user(
            username='default_role_user',
            email='default@test.com',
            password='testpass123'
            # No role specified
        )
        self.assertEqual(default_user.role, 'user')

    def test_role_choices_validation(self):
        """Test that role choices are properly defined"""
        role_choices = [choice[0] for choice in CustomUser.ROLE_CHOICES]
        expected_choices = ['superadmin', 'admin', 'user']
        
        for choice in expected_choices:
            self.assertIn(choice, role_choices)

class UserRegistrationViewTest(TestCase):
    """Test user registration functionality using OOP"""
    
    def setUp(self):
        """Set up test client and URLs"""
        self.client = Client()
        self.register_url = reverse('register')
        # Clear otp_storage before each test
        otp_storage.clear()
        
    def test_register_view_get_request(self):
        """Test GET request to register view"""
        response = self.client.get(self.register_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')
        self.assertIsInstance(response.context['form'], CustomUserRegistrationForm)

    def test_successful_user_registration(self):
        """Test successful user registration creates inactive user"""
        valid_data = {
            'username': 'newreguser',
            'email': 'newreguser@test.com',
            'role': 'user',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        
        response = self.client.post(self.register_url, valid_data)
        
        # Check user was created
        self.assertTrue(CustomUser.objects.filter(username='newreguser').exists())
        
        # Check user is inactive (waiting for OTP verification)
        user = CustomUser.objects.get(username='newreguser')
        self.assertFalse(user.is_active)
        self.assertEqual(user.role, 'user')
        self.assertEqual(user.email, 'newreguser@test.com')
        
        # Check OTP was stored
        self.assertIn('newreguser', otp_storage)
        
        # Check redirect to OTP verification
        self.assertRedirects(response, reverse('verify_otp', kwargs={'username': 'newreguser'}))

    def test_registration_with_duplicate_email(self):
        """Test registration with existing email fails"""
        # Create existing user first
        CustomUser.objects.create_user(
            username='existing_email_user',
            email='duplicate@test.com',
            password='testpass123'
        )
        
        duplicate_data = {
            'username': 'newuser_duplicate_email',
            'email': 'duplicate@test.com',  # Same email
            'role': 'user',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        
        response = self.client.post(self.register_url, duplicate_data)
        
        # Check that form has errors
        self.assertEqual(response.status_code, 200)  # Stays on same page
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('email', form.errors)
        
        # Check user was not created
        self.assertFalse(CustomUser.objects.filter(username='newuser_duplicate_email').exists())

    def test_registration_with_invalid_data(self):
        """Test registration with invalid data"""
        invalid_data = {
            'username': '',  # Empty username
            'email': 'invalid-email',  # Invalid email format
            'role': 'user',
            'password1': 'pass',  # Too short password
            'password2': 'different'  # Passwords don't match
        }
        
        response = self.client.post(self.register_url, invalid_data)
        
        self.assertEqual(response.status_code, 200)  # Stays on same page
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('username', form.errors)

class UserLoginViewTest(TestCase):
    """Test user login functionality using OOP"""
    
    def setUp(self):
        """Set up test client, URLs, and test user"""
        self.client = Client()
        self.login_url = reverse('login')
        
        # Create active test user
        self.test_user = CustomUser.objects.create_user(
            username='active_login_user',
            email='activelogin@test.com',
            password='loginpass123',
            role='admin'
        )
        self.test_user.is_active = True
        self.test_user.save()
        
        # Create inactive test user
        self.inactive_user = CustomUser.objects.create_user(
            username='inactive_login_user',
            email='inactivelogin@test.com',
            password='loginpass123',
            role='user'
        )
        self.inactive_user.is_active = False
        self.inactive_user.save()

    def test_login_view_get_request(self):
        """Test GET request to login view"""
        response = self.client.get(self.login_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertIsInstance(response.context['form'], CustomLoginForm)

    def test_successful_login_with_username(self):
        """Test successful login with username"""
        login_data = {
            'login': 'active_login_user',
            'password': 'loginpass123'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        # Check redirect to vehicle list
        self.assertRedirects(response, reverse('vehicle_list'))

    def test_successful_login_with_email(self):
        """Test successful login with email address"""
        login_data = {
            'login': 'activelogin@test.com',
            'password': 'loginpass123'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        # Check redirect to vehicle list
        self.assertRedirects(response, reverse('vehicle_list'))

    def test_login_with_invalid_credentials(self):
        """Test login with wrong password"""
        login_data = {
            'login': 'active_login_user',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, 200)  # Stays on login page
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Invalid username/email or password' in str(m) for m in messages))

    def test_login_with_inactive_user(self):
        """Test login with inactive user account"""
        login_data = {
            'login': 'inactive_login_user',
            'password': 'loginpass123'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, 200)  # Stays on login page
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('not activated' in str(m) for m in messages))

    def test_login_with_nonexistent_user(self):
        """Test login with non-existent user"""
        login_data = {
            'login': 'nonexistent_user',
            'password': 'somepassword'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, 200)  # Stays on login page
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Invalid username/email or password' in str(m) for m in messages))

class OTPVerificationViewTest(TestCase):
    """Test OTP verification functionality using OOP"""
    
    def setUp(self):
        """Set up test data for OTP verification"""
        self.client = Client()
        
        # Clear and set up OTP storage
        otp_storage.clear()
        
        # Create test user
        self.test_user = CustomUser.objects.create_user(
            username='otp_test_user',
            email='otptest@test.com',
            password='testpass123',
            role='user'
        )
        self.test_user.is_active = False
        self.test_user.save()
        
        # Add OTP to storage (simulate registration process)
        self.test_otp = 123456
        otp_storage['otp_test_user'] = {
            'otp': self.test_otp,
            'attempts': 0,
            'email': 'otptest@test.com'
        }
        
        self.verify_url = reverse('verify_otp', kwargs={'username': 'otp_test_user'})

    def tearDown(self):
        """Clean up OTP storage after each test"""
        otp_storage.clear()

    def test_verify_otp_view_get_request(self):
        """Test GET request to OTP verification view"""
        response = self.client.get(self.verify_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'otp_test_user')  # Username should be displayed

    def test_successful_otp_verification(self):
        """Test successful OTP verification activates user"""
        otp_data = {'otp': str(self.test_otp)}
        
        response = self.client.post(self.verify_url, otp_data)
        
        # Check redirect to login
        self.assertRedirects(response, reverse('login'))
        
        # Check user is now active
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.is_active)
        
        # Check OTP is removed from storage
        self.assertNotIn('otp_test_user', otp_storage)

    def test_invalid_otp_verification(self):
        """Test invalid OTP increments attempts"""
        otp_data = {'otp': '999999'}  # Wrong OTP
        
        response = self.client.post(self.verify_url, otp_data)
        
        self.assertEqual(response.status_code, 200)  # Stays on verification page
        
        # Check attempt was incremented
        self.assertEqual(otp_storage['otp_test_user']['attempts'], 1)
        
        # Check user is still inactive
        self.test_user.refresh_from_db()
        self.assertFalse(self.test_user.is_active)

class UserLogoutViewTest(TestCase):
    """Test user logout functionality using OOP"""
    
    def setUp(self):
        """Set up test client and logged-in user"""
        self.client = Client()
        self.logout_url = reverse('logout')
        
        # Create and login test user
        self.test_user = CustomUser.objects.create_user(
            username='logout_test_user',
            email='logouttest@test.com',
            password='testpass123',
            role='user'
        )
        self.test_user.is_active = True
        self.test_user.save()

    def test_logout_functionality(self):
        """Test user logout redirects and shows message"""
        # Login first
        self.client.force_login(self.test_user)
        
        # Logout
        response = self.client.get(self.logout_url)
        
        # Check redirect to login page
        self.assertRedirects(response, reverse('login'))
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Goodbye logout_test_user' in str(m) for m in messages))

class UserFormsTest(TestCase):
    """Test user forms using OOP"""
    
    def test_custom_user_registration_form_valid(self):
        """Test valid registration form"""
        valid_data = {
            'username': 'form_test_user',
            'email': 'formtest@example.com',
            'role': 'admin',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        
        form = CustomUserRegistrationForm(data=valid_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['role'], 'admin')

    def test_custom_user_registration_form_password_mismatch(self):
        """Test registration form with password mismatch"""
        invalid_data = {
            'username': 'mismatch_user',
            'email': 'mismatch@example.com',
            'role': 'user',
            'password1': 'complexpass123',
            'password2': 'differentpass123'  # Different password
        }
        
        form = CustomUserRegistrationForm(data=invalid_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_custom_login_form_valid(self):
        """Test valid login form"""
        valid_login_data = {
            'login': 'login_form_test',
            'password': 'testpass123'
        }
        
        form = CustomLoginForm(data=valid_login_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['login'], 'login_form_test')

    def test_custom_login_form_missing_fields(self):
        """Test login form with missing fields"""
        invalid_data = {'login': 'testuser'}  # Missing password
        
        form = CustomLoginForm(data=invalid_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

class UserAccessControlTest(TestCase):
    """Test user access control and security using OOP"""
    
    def setUp(self):
        """Set up test client and users for access control testing"""
        self.client = Client()
        
        # Create users with different roles
        self.superadmin = CustomUser.objects.create_user(
            username='access_superadmin',
            email='access_superadmin@test.com',
            password='testpass123',
            role='superadmin',
            is_active=True
        )
        
        self.admin = CustomUser.objects.create_user(
            username='access_admin',
            email='access_admin@test.com',
            password='testpass123',
            role='admin',
            is_active=True
        )
        
        self.user = CustomUser.objects.create_user(
            username='access_user',
            email='access_user@test.com',
            password='testpass123',
            role='user',
            is_active=True
        )

    def test_user_role_assignment_during_registration(self):
        """Test that users get assigned correct roles during registration"""
        roles_to_test = ['superadmin', 'admin', 'user']
        
        for i, role in enumerate(roles_to_test):
            username = f'role_test_{role}_user_{i}'
            user = CustomUser.objects.create_user(
                username=username,
                email=f'{username}@test.com',
                password='testpass123',
                role=role
            )
            
            self.assertEqual(user.role, role)

    def test_user_authentication_state_persistence(self):
        """Test that user authentication state persists across requests"""
        # Login user
        self.client.force_login(self.user)
        
        # Make multiple requests - both should succeed if authentication persists
        response1 = self.client.get(reverse('vehicle_list'))
        response2 = self.client.get(reverse('vehicle_list'))
        
        # Both should be successful (user remains authenticated)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
