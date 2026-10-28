"""
Custom Database models for the `voter` Django app.
"""

import datetime
import uuid
import base64
from django.utils import timezone

try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
    from cryptography.hazmat.primitives.serialization import load_pem_public_key
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from recall_server.common.mixins import OwnerlessAbstract


User = get_user_model()


class VoterProfile(models.Model):
    """
    Profile model that extends the Django User model 
    through a OneToOneField relationship.
    This follows Django's recommended approach for extending the User model.
    """
    user = models.OneToOneField(
            User,
            on_delete=models.CASCADE,
            related_name='voter_profile'
            )
    tokenized_id = models.UUIDField(
            primary_key=True,
            default=uuid.uuid4,
            editable=False
            )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional profile fields
    # profile_picture = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True)
    digital_signature = models.TextField(
            blank=True,
            help_text="Base64 encoded digital signature for document verification"
            )
    signature_public_key = models.TextField(
            blank=True,
            help_text="Public key associated with the digital signature"
            )
    signature_verified = models.BooleanField(
            default=False,
            help_text="Whether the signature has been verified"
            )
    signature_date = models.DateTimeField(
            null=True,
            blank=True,
            help_text="When the signature was added or updated"
            )
    
    # Location information for matching with representatives
    county = models.ForeignKey(
            'county.County',
            on_delete=models.SET_NULL, 
            null=True,
            blank=True,
            related_name='voters'
            )
    constituency = models.ForeignKey(
            'county.Constituency',
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            related_name='voters'
            )
    ward = models.CharField(max_length=100, blank=True)
    
    # Notification preferences
    notify_on_new_bills = models.BooleanField(default=True)
    notify_on_bill_status_change = models.BooleanField(default=True)
    notify_on_vote = models.BooleanField(default=True)
    
    # Track followed bills, legislators, and topics
    followed_bills = models.ManyToManyField(
            'laws.Bill',
            blank=True,
            related_name='followers'
            )
    followed_mps = models.ManyToManyField(
            'mps.MemberOfParliament',
            blank=True,
            related_name='followers'
            )
    followed_senators = models.ManyToManyField(
            'county.Senator',
            blank=True,
            related_name='followers'
            )
    followed_mcas = models.ManyToManyField(
            'county.MCA',
            blank=True,
            related_name='followers'
            )
    interests = models.CharField(
            max_length=500,
            blank=True,
            help_text="Comma-separated list of policy interests"
            )

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['county']),
            models.Index(fields=['constituency']),
        ]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
        
    def get_full_name(self):
        return self.user.get_full_name()
        
    def get_representatives(self):
        """Get all representatives for this voter based on location"""
        representatives = {
            'mp': None,
            'senator': None,
            'mca': None
        }
        
        if self.constituency:
            # Get MP for this constituency
            from recall_server.mps.models import MemberOfParliament
            try:
                representatives['mp'] = MemberOfParliament.objects.get(
                    constituency=self.constituency.name,
                    is_active=True
                )
            except MemberOfParliament.DoesNotExist:
                pass
                
        if self.county:
            # Get Senator for this county
            from recall_server.county.models import Senator
            try:
                representatives['senator'] = Senator.objects.get(
                    county=self.county,
                    is_active=True
                )
            except Senator.DoesNotExist:
                pass
                
        if self.ward:
            # Get MCA for this ward
            from recall_server.county.models import MCA
            try:
                representatives['mca'] = MCA.objects.get(
                    ward=self.ward,
                    is_active=True
                )
            except MCA.DoesNotExist:
                pass
                
        return representatives
        
    def get_voting_history(self):
        """Get all votes cast by this voter"""
        from recall_server.voting.models import PublicVote
        return PublicVote.objects.filter(user=self.user).select_related('bill')
        
    def get_representative_alignment(self):
        """Calculate how often this voter's votes align with their representatives"""
        from recall_server.voting.models import PublicVote, OfficialVote
        
        alignment = {
            'mp': {'aligned': 0, 'total': 0, 'percentage': 0},
            'senator': {'aligned': 0, 'total': 0, 'percentage': 0},
            'mca': {'aligned': 0, 'total': 0, 'percentage': 0}
        }
        
        # Get voter's votes
        voter_votes = PublicVote.objects.filter(user=self.user)
        
        # Get representatives
        representatives = self.get_representatives()
        
        for rep_type, rep in representatives.items():
            if not rep:
                continue
                
            for voter_vote in voter_votes:
                # Find if representative voted on this bill
                try:
                    from django.contrib.contenttypes.models import ContentType
                    content_type = ContentType.objects.get_for_model(rep)
                    
                    rep_vote = OfficialVote.objects.get(
                        bill=voter_vote.bill,
                        legislator_content_type=content_type,
                        legislator_object_id=rep.id
                    )
                    
                    alignment[rep_type]['total'] += 1
                    if rep_vote.vote == voter_vote.vote:
                        alignment[rep_type]['aligned'] += 1
                        
                except OfficialVote.DoesNotExist:
                    # Representative didn't vote on this bill
                    pass
                    
            # Calculate percentage
            if alignment[rep_type]['total'] > 0:
                alignment[rep_type]['percentage'] = round(
                    (alignment[rep_type]['aligned'] / alignment[rep_type]['total']) * 100, 2
                )
                
        return alignment

    def update_signature(self, signature, public_key):
        """
        Update the digital signature and public key.
        
        Args:
            signature (str): Base64 encoded digital signature
            public_key (str): PEM encoded public key
        """
        self.digital_signature = signature
        self.signature_public_key = public_key
        self.signature_date = timezone.now()
        self.signature_verified = False
        self.save()
        
    def verify_signature(self, message):
        """
        Verify the digital signature against a message.
        
        Args:
            message (str): The message that was signed
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            return False
            
        if not self.digital_signature or not self.signature_public_key:
            return False
            
        try:
            # Decode the signature from base64
            signature = base64.b64decode(self.digital_signature)
            
            # Load the public key
            public_key = load_pem_public_key(self.signature_public_key.encode())
            
            # Verify the signature
            public_key.verify(
                signature,
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # If we reach here, the signature is valid
            self.signature_verified = True
            self.save()
            return True

        except Exception:
            # Any error means the signature is invalid
            return False
            
    def generate_keypair(self):
        """
        Generate a new RSA keypair for digital signatures.
        
        Returns:
            tuple: (private_key_pem, public_key_pem) or (None, None) if cryptography not available
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            return None, None
            
        try:
            # Generate a private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # Get the public key
            public_key = private_key.public_key()
            
            # Serialize keys to PEM format
            from cryptography.hazmat.primitives.serialization import (
                Encoding, PrivateFormat, PublicFormat, NoEncryption
            )
            
            private_pem = private_key.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption()
            ).decode()
            
            public_pem = public_key.public_bytes(
                encoding=Encoding.PEM,
                format=PublicFormat.SubjectPublicKeyInfo
            ).decode()
            
            # Update the model with the public key
            self.signature_public_key = public_pem
            self.save()
            
            return private_pem, public_pem

        except Exception:
            return None, None
            
    def sign_message(self, message, private_key_pem):
        """
        Sign a message with the provided private key.
        
        Args:
            message (str): The message to sign
            private_key_pem (str): PEM encoded private key
            
        Returns:
            str: Base64 encoded signature or None if signing fails
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            return None
            
        try:
            from cryptography.hazmat.primitives.serialization import load_pem_private_key
            
            # Load the private key
            private_key = load_pem_private_key(
                private_key_pem.encode(),
                password=None
            )
            
            # Sign the message
            signature = private_key.sign(
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Encode the signature as base64
            signature_base64 = base64.b64encode(signature).decode()
            
            # Update the signature
            self.digital_signature = signature_base64
            self.signature_date = timezone.now()
            self.save()
            
            return signature_base64

        except Exception:
            return None


@receiver(post_save, sender=User)
def create_voter_profile(sender, instance, created, **kwargs):
    """Create a VoterProfile for every new User"""
    if created:
        VoterProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_voter_profile(sender, instance, **kwargs):
    """Save the VoterProfile when the User is saved"""
    instance.voter_profile.save()


# Keep the old Voter model for backward compatibility during migration
# This can be removed after migration is complete
# class Voter(OwnerlessAbstract):
#     """
#     Legacy model to represent a voter for the `voter` Django app.
#     This is kept for backward compatibility and will be deprecated.
#     """
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     username = models.CharField(max_length=100, unique=True)
#     password = models.CharField(max_length=128)
    
#     # Additional fields for user profile
#     profile_picture = models.URLField(blank=True, null=True)
#     bio = models.TextField(blank=True)
    
#     # Location information for matching with representatives
#     county = models.ForeignKey('county.County', on_delete=models.SET_NULL, null=True, blank=True, related_name='legacy_voters')
#     constituency = models.ForeignKey('county.Constituency', on_delete=models.SET_NULL, null=True, blank=True, related_name='legacy_voters')
#     ward = models.CharField(max_length=100, blank=True)
    
#     # Engagement metrics
#     last_login = models.DateTimeField(null=True, blank=True)
#     date_joined = models.DateTimeField(auto_now_add=True)
#     is_verified = models.BooleanField(default=False)
    
#     class Meta:
#         indexes = [
#             models.Index(fields=['email']),
#             models.Index(fields=['username']),
#         ]

#     def __str__(self):
#         return f"{self.first_name} {self.last_name}"
