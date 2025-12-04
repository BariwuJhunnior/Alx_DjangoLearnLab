from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate, APIRequestFactory, APIClient
from django.contrib.auth.models import User
from .models import Book, Author

class BookAPITest(APITestCase):

  def setUp(self):
    self.user = User.objects.create_user(username='testuser', password='password123')
    self.anonymous_user = User.objects.create_user(username='anon', password='password123')
    self.client.login(username='testuser', password='password123')

    # Create Author objects for ForeignKey relationships
    self.adams = Author.objects.create(name="Douglas Adams")
    self.orwell = Author.objects.create(name="George Orwell")

    self.detail_url = reverse('book-detail', kwargs={'pk': self.book1.pk})

    self.list_url = reverse('book-list')

    self.book1 = Book.objects.create(
      title="The Hitchhiker's Guide",
      author=self.adams,
      publication_year="1979-10-12",
      user=self.user
    )

    self.book2 = Book.objects.create(
      title="1984",
      author="George Orwell",
      publication_year=1949,
      user=self.user
    )

    self.valid_payload = {
      'title': 'New Book Title',
      'author': 'Jane Doe',
      'publication_year': 2020,
      'user': self.user
    }

  
  # --- Test Permissions and Status Codes ---

  ## 1. Test Read-Only Access (Permissions)
  def test_list_view_accessible_by_anonymous_user(self):
    """Anonymous users should be able to GET the list view (Read-only)."""
    response = self.client.get(self.list_url)
    #We expect a successful response (HHTP 200 OK)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(len(response.data), 2)

  def test_create_view_denied_to_anonymous_user(self):
    """Anonymous users should be denied POST access (Write permission check)."""
    response = self.client.post(self.list_url, self.valid_payload)
    #We expect authentication to fail (HTTP 401 Unauthorized, if using IsAuthenticated)
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    self.assertEqual(Book.objects.count(), 2)

  def test_update_view_denied_to_anonymouse_user(self):
    """Anonymous users should be denied PUT/PATCH access."""
    response = self.client.put(self.detail_url, {'title': 'Updated Title'})
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

  def test_create_book_by_authenticated_user(self):
    """Authenticated users should be able to successfully POST data."""
    #Log in the test user
    self.client.force_authenticate(user=self.user)

    response = self.client.post(self.list_url, self.valid_payload, format='json')

    #Check status code
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #Check database count
    self.assertEqual(Book.objects.count(), 3)
    #Check the response data integrity
    self.assertEqual(response.data['title'],  'New Book Title')
    self.assertEqual(response.data['author'], 'Jane Doe')

  def test_upddate_book_data_integrity(self):
    """Authenticated users should be able to update fields correctly."""
    self.client.force_authenticate(user=self.user)
    updated_data = {'title': 'Updated Title', 'author': 'Adams', 'publication_year': 2000, 'user': self.user.id}
    response = self.client.put(self.detail_url, updated_data, format='json')

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.book.refresh_from_db()
    self.assertEqual(self.book.title, 'Updated Title')
    self.assertEqual(self.book.author, 'Adams')
    #Verify the change in response
    self.assertEqual(response.data['title'], 'Updated Title')
    #Verify the change in the database
    self.book1.refresh_from_db()
    self.assertEqual(self.book1.title, 'Updated Title')

  def test_delete_book_by_authenticated_user(self):
    """Authenticated users should be able to delete an object."""
    self.client.force_authenticate(user=self.user)

    response = self.client.delete(self.detail_url)
    
    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    self.assertEqual(Book.objects.count(), 1)

  # --- Test Filtering, Searching, and Ordering ---
  def test_filtering_by_author(self):
    """Should correctly filter results based on the author query parameter."""
    response = self.client.get(self.list_url + '?author=Adams')
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(len(response.data),1)
    self.assertEqual(response.data[0]['title'], "The Hitchhiker's Guide")


  def test_ordering_by_title_descending(self):
    """Should correctly order results based on the ordering query parameter."""
    response = self.client.get(self.list_url + '?ordering=-title') # -title = descending order

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # Check that 'The Hitchhiker's Guide' (T) comes before '1984' (1) alphabetically descending
    self.assertEqual(response.data[0]['title'], "The Hichhiker's Guide")
    self.assertEqual(response.data[1]['title'], "1984")