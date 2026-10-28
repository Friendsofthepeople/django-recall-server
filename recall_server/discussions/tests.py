from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient
from rest_framework import status

from recall_server.discussions.models import Discussion, Comment, Reaction
from recall_server.laws.models import Bill


class DiscussionModelTest(TestCase):
    """Test cases for the Discussion model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a bill to associate with discussion
        self.bill = Bill.objects.create(
            bill_number='TEST-001',
            title='Test Bill',
            description='A test bill',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='draft',
            bill_type='private'
        )
        
        # Get content type for Bill
        self.content_type = ContentType.objects.get_for_model(Bill)
        
        # Create a discussion
        self.discussion = Discussion.objects.create(
            title="Test Discussion",
            content="This is a test discussion about a bill.",
            author=self.user,
            content_type=self.content_type,
            object_id=self.bill.id
        )
        
    def test_discussion_creation(self):
        """Test creating a discussion object."""
        self.assertEqual(self.discussion.title, "Test Discussion")
        self.assertEqual(self.discussion.content, "This is a test discussion about a bill.")
        self.assertEqual(self.discussion.author, self.user)
        self.assertEqual(self.discussion.content_type, self.content_type)
        self.assertEqual(self.discussion.object_id, self.bill.id)
        self.assertIsNotNone(self.discussion.created_at)
        self.assertIsNotNone(self.discussion.updated_at)
        
    def test_string_representation(self):
        """Test string representation of a discussion."""
        self.assertEqual(str(self.discussion), "Test Discussion")
        
    def test_generic_relation(self):
        """Test generic foreign key relationship."""
        self.assertEqual(self.discussion.content_object, self.bill)


class CommentModelTest(TestCase):
    """Test cases for the Comment model."""
    
    def setUp(self):
        """Set up test data."""
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password123'
        )
        
        # Create a bill
        self.bill = Bill.objects.create(
            bill_number='TEST-001',
            title='Test Bill',
            description='A test bill',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='draft',
            bill_type='private'
        )
        
        # Get content type for Bill
        self.content_type = ContentType.objects.get_for_model(Bill)
        
        # Create a discussion
        self.discussion = Discussion.objects.create(
            title="Test Discussion",
            content="This is a test discussion about a bill.",
            author=self.user,
            content_type=self.content_type,
            object_id=self.bill.id
        )
        
        # Create comments
        self.comment = Comment.objects.create(
            content="This is a test comment.",
            author=self.user,
            content_type=ContentType.objects.get_for_model(Discussion),
            object_id=self.discussion.id
        )
        
        # Create a reply to the comment
        self.reply = Comment.objects.create(
            content="This is a reply to the test comment.",
            author=self.user2,
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=self.comment.id,
            parent=self.comment
        )
        
    def test_comment_creation(self):
        """Test creating a comment object."""
        self.assertEqual(self.comment.content, "This is a test comment.")
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.content_type, ContentType.objects.get_for_model(Discussion))
        self.assertEqual(self.comment.object_id, self.discussion.id)
        self.assertIsNone(self.comment.parent)
        self.assertIsNotNone(self.comment.created_at)
        
    def test_reply_creation(self):
        """Test creating a reply (nested comment)."""
        self.assertEqual(self.reply.content, "This is a reply to the test comment.")
        self.assertEqual(self.reply.author, self.user2)
        self.assertEqual(self.reply.content_type, ContentType.objects.get_for_model(Comment))
        self.assertEqual(self.reply.object_id, self.comment.id)
        self.assertEqual(self.reply.parent, self.comment)
        
    def test_string_representation(self):
        """Test string representation of a comment."""
        self.assertEqual(str(self.comment), "Comment by testuser")
        
    def test_generic_relation(self):
        """Test generic foreign key relationship."""
        self.assertEqual(self.comment.content_object, self.discussion)
        self.assertEqual(self.reply.content_object, self.comment)


class ReactionModelTest(TestCase):
    """Test cases for the Reaction model."""
    
    def setUp(self):
        """Set up test data."""
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password123'
        )
        
        # Create a bill
        self.bill = Bill.objects.create(
            bill_number='TEST-001',
            title='Test Bill',
            description='A test bill',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='draft',
            bill_type='private'
        )
        
        # Get content type for Bill
        self.bill_content_type = ContentType.objects.get_for_model(Bill)
        
        # Create a discussion
        self.discussion = Discussion.objects.create(
            title="Test Discussion",
            content="This is a test discussion about a bill.",
            author=self.user,
            content_type=self.bill_content_type,
            object_id=self.bill.id
        )
        
        # Get content type for Discussion
        self.discussion_content_type = ContentType.objects.get_for_model(Discussion)
        
        # Create reactions
        self.reaction_like = Reaction.objects.create(
            reaction_type='like',
            user=self.user,
            content_type=self.discussion_content_type,
            object_id=self.discussion.id
        )
        
        self.reaction_dislike = Reaction.objects.create(
            reaction_type='dislike',
            user=self.user2,
            content_type=self.discussion_content_type,
            object_id=self.discussion.id
        )
        
    def test_reaction_creation(self):
        """Test creating reaction objects."""
        self.assertEqual(self.reaction_like.reaction_type, 'like')
        self.assertEqual(self.reaction_like.user, self.user)
        self.assertEqual(self.reaction_like.content_type, self.discussion_content_type)
        self.assertEqual(self.reaction_like.object_id, self.discussion.id)
        
        self.assertEqual(self.reaction_dislike.reaction_type, 'dislike')
        self.assertEqual(self.reaction_dislike.user, self.user2)
        
    def test_string_representation(self):
        """Test string representation of a reaction."""
        self.assertEqual(str(self.reaction_like), "like by testuser")
        
    def test_generic_relation(self):
        """Test generic foreign key relationship."""
        self.assertEqual(self.reaction_like.content_object, self.discussion)
        
    def test_unique_constraint(self):
        """Test that a user can only react once to an object."""
        # Try to create another reaction from the same user to the same object
        with self.assertRaises(Exception):  # Could be IntegrityError or ValidationError
            Reaction.objects.create(
                reaction_type='love',  # Different reaction type
                user=self.user,  # Same user
                content_type=self.discussion_content_type,  # Same content type
                object_id=self.discussion.id  # Same object
            )


class DiscussionSerializerTest(TestCase):
    """Test cases for Discussion serializer."""
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a bill
        self.bill = Bill.objects.create(
            bill_number='TEST-001',
            title='Test Bill',
            description='A test bill',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='draft',
            bill_type='private'
        )
        
        # Get content type for Bill
        self.content_type = ContentType.objects.get_for_model(Bill)
        
        # Create a discussion
        self.discussion = Discussion.objects.create(
            title="Test Discussion",
            content="This is a test discussion about a bill.",
            author=self.user,
            content_type=self.content_type,
            object_id=self.bill.id
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
    def test_discussion_serialization(self):
        """Test discussion serialization."""
        url = reverse('discussion-detail', kwargs={'pk': self.discussion.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Discussion")
        self.assertEqual(response.data['content'], "This is a test discussion about a bill.")
        self.assertEqual(response.data['author'], self.user.id)
        self.assertEqual(response.data['content_type'], self.content_type.id)
        self.assertEqual(response.data['object_id'], str(self.bill.id))


class CommentSerializerTest(TestCase):
    """Test cases for Comment serializer."""
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password123'
        )
        
        # Create a bill
        self.bill = Bill.objects.create(
            bill_number='TEST-001',
            title='Test Bill',
            description='A test bill',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='draft',
            bill_type='private'
        )
        
        # Get content type for Bill
        self.bill_content_type = ContentType.objects.get_for_model(Bill)
        
        # Create a discussion
        self.discussion = Discussion.objects.create(
            title="Test Discussion",
            content="This is a test discussion about a bill.",
            author=self.user,
            content_type=self.bill_content_type,
            object_id=self.bill.id
        )
        
        # Get content type for Discussion
        self.discussion_content_type = ContentType.objects.get_for_model(Discussion)
        
        # Create a comment
        self.comment = Comment.objects.create(
            content="This is a test comment.",
            author=self.user,
            content_type=self.discussion_content_type,
            object_id=self.discussion.id
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
    def test_comment_serialization(self):
        """Test comment serialization."""
        url = reverse('comment-detail', kwargs={'pk': self.comment.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], "This is a test comment.")
        self.assertEqual(response.data['author'], self.user.id)
        self.assertEqual(response.data['content_type'], self.discussion_content_type.id)
        self.assertEqual(response.data['object_id'], str(self.discussion.id))


class ReactionSerializerTest(TestCase):
    """Test cases for Reaction serializer."""
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a bill
        self.bill = Bill.objects.create(
            bill_number='TEST-001',
            title='Test Bill',
            description='A test bill',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='draft',
            bill_type='private'
        )
        
        # Get content type for Bill
        self.bill_content_type = ContentType.objects.get_for_model(Bill)
        
        # Create a discussion
        self.discussion = Discussion.objects.create(
            title="Test Discussion",
            content="This is a test discussion about a bill.",
            author=self.user,
            content_type=self.bill_content_type,
            object_id=self.bill.id
        )
        
        # Get content type for Discussion
        self.discussion_content_type = ContentType.objects.get_for_model(Discussion)
        
        # Create a reaction
        self.reaction = Reaction.objects.create(
            reaction_type='like',
            user=self.user,
            content_type=self.discussion_content_type,
            object_id=self.discussion.id
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
    def test_reaction_serialization(self):
        """Test reaction serialization."""
        url = reverse('reaction-detail', kwargs={'pk': self.reaction.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reaction_type'], 'like')
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['content_type'], self.discussion_content_type.id)
        self.assertEqual(response.data['object_id'], str(self.discussion.id))


class DiscussionViewSetTest(TestCase):
    """Test cases for Discussion ViewSet."""
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password123'
        )
        
        # Create a bill
        self.bill = Bill.objects.create(
            bill_number='TEST-001',
            title='Test Bill',
            description='A test bill',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='draft',
            bill_type='private'
        )
        
        # Get content type for Bill
        self.content_type = ContentType.objects.get_for_model(Bill)
        
        # Create a discussion
        self.discussion = Discussion.objects.create(
            title="Test Discussion",
            content="This is a test discussion about a bill.",
            author=self.user,
            content_type=self.content_type,
            object_id=self.bill.id
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
    def test_list_discussions(self):
        """Test listing discussions."""
        url = reverse('discussion-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_discussion(self):
        """Test retrieving a discussion."""
        url = reverse('discussion-detail', kwargs={'pk': self.discussion.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Discussion")
        
    def test_create_discussion(self):
        """Test creating a discussion."""
        url = reverse('discussion-list')
        data = {
            'title': 'New Discussion',
            'content': 'This is a new discussion about the bill.',
            'author': self.user.id,
            'content_type': self.content_type.id,
            'object_id': self.bill.id
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Discussion.objects.count(), 2)
        self.assertEqual(Discussion.objects.get(title='New Discussion').content, 'This is a new discussion about the bill.')
        
    def test_update_own_discussion(self):
        """Test updating own discussion."""
        url = reverse('discussion-detail', kwargs={'pk': self.discussion.pk})
        data = {
            'content': 'Updated discussion content'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.discussion.refresh_from_db()
        self.assertEqual(self.discussion.content, 'Updated discussion content')
        
    def test_update_others_discussion(self):
        """Test that users cannot update others' discussions."""
        # Authenticate as another user
        self.client.force_authenticate(user=self.user2)
        
        url = reverse('discussion-detail', kwargs={'pk': self.discussion.pk})
        data = {
            'content': 'Unauthorized update'
        }
        response = self.client.patch(url, data)
        
        # Should be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.discussion.refresh_from_db()
        self.assertEqual(self.discussion.content, "This is a test discussion about a bill.")  # Unchanged
        
    def test_delete_own_discussion(self):
        """Test deleting own discussion."""
        url = reverse('discussion-detail', kwargs={'pk': self.discussion.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Discussion.objects.count(), 0)
        
    def test_delete_others_discussion(self):
        """Test that users cannot delete others' discussions."""
        # Authenticate as another user
        self.client.force_authenticate(user=self.user2)
        
        url = reverse('discussion-detail', kwargs={'pk': self.discussion.pk})
        response = self.client.delete(url)
        
        # Should be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Discussion.objects.count(), 1)  # Still exists
        
    def test_filter_discussions_by_content_object(self):
        """Test filtering discussions by content object."""
        url = reverse('discussion-list') + f'?content_type={self.content_type.id}&object_id={self.bill.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Test Discussion")


class CommentViewSetTest(TestCase):
    """Test cases for Comment ViewSet."""
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password123'
        )
        
        # Create a bill
        self.bill = Bill.objects.create(
            bill_number='TEST-001',
            title='Test Bill',
            description='A test bill',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='draft',
            bill_type='private'
        )
        
        # Get content type for Bill
        self.bill_content_type = ContentType.objects.get_for_model(Bill)
        
        # Create a discussion
        self.discussion = Discussion.objects.create(
            title="Test Discussion",
            content="This is a test discussion about a bill.",
            author=self.user,
            content_type=self.bill_content_type,
            object_id=self.bill.id
        )
        
        # Get content type for Discussion
        self.discussion_content_type = ContentType.objects.get_for_model(Discussion)
        
        # Create a comment
        self.comment = Comment.objects.create(
            content="This is a test comment.",
            author=self.user,
            content_type=self.discussion_content_type,
            object_id=self.discussion.id
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
    def test_list_comments(self):
        """Test listing comments."""
        url = reverse('comment-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_comment(self):
        """Test retrieving a comment."""
        url = reverse('comment-detail', kwargs={'pk': self.comment.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], "This is a test comment.")
        
    def test_create_comment(self):
        """Test creating a comment."""
        url = reverse('comment-list')
        data = {
            'content': 'This is a new comment.',
            'author': self.user.id,
            'content_type': self.discussion_content_type.id,
            'object_id': self.discussion.id
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        
    def test_create_reply(self):
        """Test creating a reply to a comment."""
        url = reverse('comment-list')
        data = {
            'content': 'This is a reply to the comment.',
            'author': self.user.id,
            'content_type': ContentType.objects.get_for_model(Comment).id,
            'object_id': self.comment.id,
            'parent': self.comment.id
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        
        # Verify it's a reply
        reply = Comment.objects.get(content='This is a reply to the comment.')
        self.assertEqual(reply.parent, self.comment)
        
    def test_update_own_comment(self):
        """Test updating own comment."""
        url = reverse('comment-detail', kwargs={'pk': self.comment.pk})
        data = {
            'content': 'Updated comment content'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Updated comment content')
        
    def test_delete_own_comment(self):
        """Test deleting own comment."""
        url = reverse('comment-detail', kwargs={'pk': self.comment.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)
        
    def test_filter_comments_by_content_object(self):
        """Test filtering comments by content object."""
        url = reverse('comment-list') + f'?content_type={self.discussion_content_type.id}&object_id={self.discussion.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], "This is a test comment.")


class ReactionViewSetTest(TestCase):
    """Test cases for Reaction ViewSet."""
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password123'
        )
        
        # Create a bill
        self.bill = Bill.objects.create(
            bill_number='TEST-001',
            title='Test Bill',
            description='A test bill',
            sponsor='Test Sponsor',
            proposer=self.user,
            status='draft',
            bill_type='private'
        )
        
        # Get content type for Bill
        self.bill_content_type = ContentType.objects.get_for_model(Bill)
        
        # Create a discussion
        self.discussion = Discussion.objects.create(
            title="Test Discussion",
            content="This is a test discussion about a bill.",
            author=self.user,
            content_type=self.bill_content_type,
            object_id=self.bill.id
        )
        
        # Get content type for Discussion
        self.discussion_content_type = ContentType.objects.get_for_model(Discussion)
        
        # Create a reaction
        self.reaction = Reaction.objects.create(
            reaction_type='like',
            user=self.user,
            content_type=self.discussion_content_type,
            object_id=self.discussion.id
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
    def test_list_reactions(self):
        """Test listing reactions."""
        url = reverse('reaction-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_reaction(self):
        """Test retrieving a reaction."""
        url = reverse('reaction-detail', kwargs={'pk': self.reaction.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reaction_type'], 'like')
        
    def test_create_reaction(self):
        """Test creating a reaction from another user."""
        # Authenticate as another user
        self.client.force_authenticate(user=self.user2)
        
        url = reverse('reaction-list')
        data = {
            'reaction_type': 'dislike',
            'user': self.user2.id,
            'content_type': self.discussion_content_type.id,
            'object_id': self.discussion.id
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reaction.objects.count(), 2)
        self.assertEqual(Reaction.objects.get(user=self.user2).reaction_type, 'dislike')
        
    def test_update_reaction(self):
        """Test updating own reaction."""
        url = reverse('reaction-detail', kwargs={'pk': self.reaction.pk})
        data = {
            'reaction_type': 'love'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reaction.refresh_from_db()
        self.assertEqual(self.reaction.reaction_type, 'love')
        
    def test_delete_reaction(self):
        """Test deleting own reaction."""
        url = reverse('reaction-detail', kwargs={'pk': self.reaction.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Reaction.objects.count(), 0)
        
    def test_filter_reactions_by_content_object(self):
        """Test filtering reactions by content object."""
        url = reverse('reaction-list') + f'?content_type={self.discussion_content_type.id}&object_id={self.discussion.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['reaction_type'], 'like')
        
    def test_filter_reactions_by_user(self):
        """Test filtering reactions by user."""
        url = reverse('reaction-list') + f'?user={self.user.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['reaction_type'], 'like')
