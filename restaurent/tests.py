from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from common.models import RestaurentEntity, Product, Variant, Category
from .models import RestaurentMenu

User = get_user_model()


class RestaurantListTestCase(APITestCase):
    def setUp(self):
        # Create test restaurants
        self.restaurant1 = RestaurentEntity.objects.create(
            name='Pizza Palace',
            description='Best pizza in town',
            address='123 Main St',
            is_available=True
        )

        self.restaurant2 = RestaurentEntity.objects.create(
            name='Burger House',
            description='Delicious burgers and fries',
            address='456 Oak Ave',
            is_available=True
        )

        self.restaurant3 = RestaurentEntity.objects.create(
            name='Closed Restaurant',
            description='Currently closed',
            address='789 Pine St',
            is_available=False
        )

    def test_restaurant_list_success(self):
        """Test successful restaurant listing"""
        url = reverse('restaurant-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # All restaurants returned

        # Check first restaurant data (ordered by name, so "Burger House" comes first)
        restaurant_data = response.data[0]
        self.assertEqual(restaurant_data['name'], 'Burger House')
        self.assertEqual(restaurant_data['description'], 'Delicious burgers and fries')
        self.assertEqual(restaurant_data['address'], '456 Oak Ave')
        self.assertEqual(restaurant_data['is_available'], True)

    def test_restaurant_list_filter_by_availability(self):
        """Test filtering restaurants by availability"""
        url = reverse('restaurant-list')
        response = self.client.get(url, {'is_available': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only available restaurants

        # Check that all returned restaurants are available
        for restaurant in response.data:
            self.assertTrue(restaurant['is_available'])

    def test_restaurant_list_filter_unavailable(self):
        """Test filtering for unavailable restaurants"""
        url = reverse('restaurant-list')
        response = self.client.get(url, {'is_available': 'false'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only unavailable restaurant
        self.assertEqual(response.data[0]['name'], 'Closed Restaurant')
        self.assertFalse(response.data[0]['is_available'])

    def test_restaurant_list_search_by_name(self):
        """Test searching restaurants by name"""
        url = reverse('restaurant-list')
        response = self.client.get(url, {'search': 'pizza'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Pizza Palace')

    def test_restaurant_list_search_by_description(self):
        """Test searching restaurants by description"""
        url = reverse('restaurant-list')
        response = self.client.get(url, {'search': 'burgers'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Burger House')

    def test_restaurant_list_combined_filters(self):
        """Test combining availability and search filters"""
        url = reverse('restaurant-list')
        response = self.client.get(url, {
            'is_available': 'true',
            'search': 'pizza'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Pizza Palace')
        self.assertTrue(response.data[0]['is_available'])

    def test_restaurant_list_no_authentication_required(self):
        """Test that no authentication is required for restaurant list"""
        url = reverse('restaurant-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should work without authentication


class AdminMenuItemsListTestCase(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            mobile_number='9876543210',
            is_staff=True
        )

        # Create test data
        self.category = Category.objects.create(
            name='Test Category',
            type='food'
        )

        self.restaurant = RestaurentEntity.objects.create(
            name='Test Restaurant',
            address='Test Address'
        )

        self.product = Product.objects.create(
            name='Test Product',
            category=self.category
        )

        self.variant = Variant.objects.create(
            product=self.product,
            size='Medium',
            price=100.00,
            type='size'
        )

        self.menu_item = RestaurentMenu.objects.create(
            restaurent=self.restaurant,
            product=self.product,
            is_available=True,
            is_veg=True,
            default_variant=self.variant
        )

        # Create second restaurant for filtering tests
        self.restaurant2 = RestaurentEntity.objects.create(
            name='Another Restaurant',
            address='Another Address'
        )

        self.product2 = Product.objects.create(
            name='Another Product',
            category=self.category
        )

        self.variant2 = Variant.objects.create(
            product=self.product2,
            size='Large',
            price=150.00,
            type='size'
        )

        self.menu_item2 = RestaurentMenu.objects.create(
            restaurent=self.restaurant2,
            product=self.product2,
            is_available=True,
            is_veg=False,
            default_variant=self.variant2
        )

    def test_admin_menu_items_list_all(self):
        """Test that admin can access all menu items without filters"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-menu-items-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two restaurants

        # Check first restaurant
        restaurant_data = response.data[0]
        self.assertEqual(restaurant_data['restaurent_name'], 'Another Restaurant')
        self.assertEqual(len(restaurant_data['products']), 1)

        # Check second restaurant
        restaurant_data = response.data[1]
        self.assertEqual(restaurant_data['restaurent_name'], 'Test Restaurant')
        self.assertEqual(len(restaurant_data['products']), 1)

    def test_admin_menu_items_list_filter_by_id(self):
        """Test filtering menu items by restaurant ID"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-menu-items-list')
        response = self.client.get(url, {'restaurent_id': self.restaurant.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        restaurant_data = response.data[0]
        self.assertEqual(restaurant_data['restaurent_entity_id'], self.restaurant.id)
        self.assertEqual(restaurant_data['restaurent_name'], 'Test Restaurant')
        self.assertEqual(len(restaurant_data['products']), 1)

        product_data = restaurant_data['products'][0]
        self.assertEqual(product_data['menu_item_id'], self.menu_item.id)
        self.assertEqual(product_data['product_id'], self.product.id)
        self.assertEqual(product_data['product_name'], self.product.name)
        self.assertEqual(product_data['is_available'], True)
        self.assertEqual(product_data['is_veg'], True)
        self.assertIsNotNone(product_data['default_variant'])
        self.assertEqual(product_data['default_variant']['variant_id'], self.variant.id)
        self.assertEqual(product_data['default_variant']['size'], self.variant.size)

    def test_admin_menu_items_list_filter_by_name(self):
        """Test filtering menu items by restaurant name"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-menu-items-list')
        response = self.client.get(url, {'restaurent_name': 'Test'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        restaurant_data = response.data[0]
        self.assertEqual(restaurant_data['restaurent_name'], 'Test Restaurant')

    def test_admin_menu_items_list_filter_by_name_case_insensitive(self):
        """Test filtering menu items by restaurant name (case insensitive)"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-menu-items-list')
        response = self.client.get(url, {'restaurent_name': 'another'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        restaurant_data = response.data[0]
        self.assertEqual(restaurant_data['restaurent_name'], 'Another Restaurant')

    def test_admin_menu_items_list_invalid_restaurant_id(self):
        """Test error handling for invalid restaurant ID"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-menu-items-list')
        response = self.client.get(url, {'restaurent_id': 'invalid'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_admin_menu_items_list_nonexistent_restaurant_id(self):
        """Test filtering with non-existent restaurant ID returns empty list"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-menu-items-list')
        response = self.client.get(url, {'restaurent_id': 9999})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_admin_menu_items_list_unauthorized(self):
        """Test that non-admin users cannot access menu items list"""
        regular_user = User.objects.create_user(
            mobile_number='9876543211',
            is_staff=False
        )
        self.client.force_authenticate(user=regular_user)
        url = reverse('admin-menu-items-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminMenuItemCRUDTestCase(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            mobile_number='9876543210',
            is_staff=True
        )

        # Create regular user
        self.regular_user = User.objects.create_user(
            mobile_number='9876543211',
            is_staff=False
        )

        # Create test data
        self.category = Category.objects.create(
            name='Test Category',
            type='food'
        )

        self.restaurant = RestaurentEntity.objects.create(
            name='Test Restaurant',
            address='Test Address'
        )

        self.product = Product.objects.create(
            name='Test Product',
            category=self.category
        )

        self.variant1 = Variant.objects.create(
            product=self.product,
            size='Medium',
            price=100.00,
            type='size'
        )

        self.variant2 = Variant.objects.create(
            product=self.product,
            size='Large',
            price=150.00,
            type='size'
        )

        self.menu_item = RestaurentMenu.objects.create(
            restaurent=self.restaurant,
            product=self.product,
            is_available=True,
            is_veg=True,
            default_variant=self.variant1
        )

    def test_admin_add_menu_item_success(self):
        """Test successful menu item creation"""
        # Create another product for testing
        product2 = Product.objects.create(
            name='Another Product',
            category=self.category
        )

        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-add-menu-item')
        data = {
            'product_id': product2.id,
            'restaurent_id': self.restaurant.id,
            'is_available': True,
            'is_veg': False,
            'default_variant_id': None
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('menu_item', response.data)

    def test_admin_add_menu_item_duplicate(self):
        """Test duplicate menu item creation fails"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-add-menu-item')
        data = {
            'product_id': self.product.id,
            'restaurent_id': self.restaurant.id,
            'is_available': True,
            'is_veg': False
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_admin_update_menu_item_success(self):
        """Test successful menu item update"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-update-menu-item', kwargs={'menu_item_id': self.menu_item.id})
        data = {
            'is_available': False,
            'is_veg': False,
            'default_variant_id': self.variant2.id
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('menu_item', response.data)

        # Verify the update
        self.menu_item.refresh_from_db()
        self.assertEqual(self.menu_item.is_available, False)
        self.assertEqual(self.menu_item.is_veg, False)
        self.assertEqual(self.menu_item.default_variant.id, self.variant2.id)

    def test_admin_update_menu_item_invalid_variant(self):
        """Test update with invalid variant fails"""
        # Create variant for different product
        other_product = Product.objects.create(
            name='Other Product',
            category=self.category
        )
        other_variant = Variant.objects.create(
            product=other_product,
            size='Small',
            price=50.00,
            type='size'
        )

        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-update-menu-item', kwargs={'menu_item_id': self.menu_item.id})
        data = {
            'default_variant_id': other_variant.id
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_admin_update_menu_item_not_found(self):
        """Test update non-existent menu item"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-update-menu-item', kwargs={'menu_item_id': 9999})
        data = {'is_available': False}
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_delete_menu_item_success(self):
        """Test successful menu item deletion"""
        menu_item_id = self.menu_item.id

        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-delete-menu-item', kwargs={'menu_item_id': menu_item_id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('deleted_item', response.data)

        # Verify deletion
        self.assertFalse(RestaurentMenu.objects.filter(id=menu_item_id).exists())

    def test_admin_delete_menu_item_not_found(self):
        """Test delete non-existent menu item"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-delete-menu-item', kwargs={'menu_item_id': 9999})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_regular_user_cannot_crud_menu_items(self):
        """Test that regular users cannot perform CRUD operations"""
        self.client.force_authenticate(user=self.regular_user)

        # Test add
        add_url = reverse('admin-add-menu-item')
        response = self.client.post(add_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test update
        update_url = reverse('admin-update-menu-item', kwargs={'menu_item_id': self.menu_item.id})
        response = self.client.put(update_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test delete
        delete_url = reverse('admin-delete-menu-item', kwargs={'menu_item_id': self.menu_item.id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
