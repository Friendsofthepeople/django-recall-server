"""
Custom views for the `voter` Django app.
"""

from django.contrib.auth import get_user_model
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from recall_server.voter.models import VoterProfile
from recall_server.voter.serializers import (
    VoterSerializer,
    VoterProfileSerializer,
    VoterProfileDetailSerializer,
)


User = get_user_model()


class VoterProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for the VoterProfile model.
    """
    queryset = VoterProfile.objects.all()
    serializer_class = VoterProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'me':
            return VoterProfileDetailSerializer
        return VoterProfileSerializer
    
    def get_queryset(self):
        # Regular users can only see their own profile
        user = self.request.user
        if not user.is_staff:
            return VoterProfile.objects.filter(user=self.request.user.id)
        return VoterProfile.objects.all()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get the current user's profile
        """
        profile = request.user.voter_profile
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def follow_bill(self, request, pk=None):
        """
        Follow a bill
        """
        profile = self.get_object()
        bill_id = request.data.get('bill_id')
        
        if not bill_id:
            return Response(
                    {"detail": "No bill ID provided."},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            
        from recall_server.laws.models import Bill
        try:
            bill = Bill.objects.get(bill_id=bill_id)
            profile.followed_bills.add(bill)
            return Response({"detail": "Bill followed successfully."})
        except Bill.DoesNotExist:
            return Response(
                    {"detail": "Bill not found."},
                    status=status.HTTP_404_NOT_FOUND
                    )
    
    @action(detail=True, methods=['post'])
    def unfollow_bill(self, request, pk=None):
        """
        Unfollow a bill
        """
        profile = self.get_object()
        bill_id = request.data.get('bill_id')
        
        if not bill_id:
            return Response(
                    {"detail": "No bill ID provided."},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            
        from recall_server.laws.models import Bill
        try:
            bill = Bill.objects.get(bill_id=bill_id)
            profile.followed_bills.remove(bill)
            return Response({"detail": "Bill unfollowed successfully."})
        except Bill.DoesNotExist:
            return Response(
                    {"detail": "Bill not found."},
                    status=status.HTTP_404_NOT_FOUND
                    )
    
    @action(detail=True, methods=['post'])
    def generate_signature_keypair(self, request, pk=None):
        """
        Generate a new keypair for digital signatures
        """
        profile = self.get_object()
        private_key, public_key = profile.generate_keypair()
        
        if not private_key or not public_key:
            return Response(
                {"detail": "Failed to generate keypair.\
                    Cryptography library may not be available."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Return only the private key once, as it won't be stored on the server
        return Response({
            "private_key": private_key,
            "public_key": public_key,
            "message": "Store your private key securely. \
                    It will not be available again."
        })
        
    @action(detail=True, methods=['post'])
    def sign_document(self, request, pk=None):
        """
        Sign a document using the provided private key
        """
        profile = self.get_object()
        message = request.data.get('message')
        private_key = request.data.get('private_key')
        
        if not message or not private_key:
            return Response(
                {"detail": "Both message and private_key are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        signature = profile.sign_message(message, private_key)
        
        if not signature:
            return Response(
                {"detail": "Failed to sign the message."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        return Response({
            "signature": signature,
            "public_key": profile.signature_public_key,
            "date": profile.signature_date
        })
        
    @action(detail=True, methods=['post'])
    def verify_signature(self, request, pk=None):
        """
        Verify a signature against a message
        """
        profile = self.get_object()
        message = request.data.get('message')
        
        if not message:
            return Response(
                {"detail": "Message is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not profile.digital_signature or not profile.signature_public_key:
            return Response(
                {"detail": "No signature available for verification."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        is_valid = profile.verify_signature(message)
        
        return Response({
            "is_valid": is_valid,
            "verified": profile.signature_verified
        })
        
    @action(detail=True, methods=['post'])
    def update_signature(self, request, pk=None):
        """
        Update the digital signature and public key
        """
        profile = self.get_object()
        signature = request.data.get('signature')
        public_key = request.data.get('public_key')
        
        if not signature or not public_key:
            return Response(
                {"detail": "Both signature and public_key are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        profile.update_signature(signature, public_key)
        
        return Response({
            "detail": "Signature updated successfully.",
            "signature_date": profile.signature_date
        })


class UserRegisterView(APIView):
    """
    API view for user registration.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = VoterProfileSerializer(data=request.data)
        if serializer.is_valid():
            profile = serializer.save()
            return Response(VoterProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Legacy view for backward compatibility
# class VoterRegisterView(APIView):
#     """
#     Legacy API view for voter registration.
#     This is kept for backward compatibility and will be deprecated.
#     """
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         serializer = VoterSerializer(data=request.data)
#         if serializer.is_valid():
#             voter = serializer.save()
            
#             # Also create a User and VoterProfile for this Voter
#             user = User.objects.create(
#                 username=voter.username,
#                 email=voter.email,
#                 password=voter.password,  # Note: This is already hashed
#                 first_name=voter.first_name,
#                 last_name=voter.last_name
#             )
            
#             # Update the VoterProfile
#             profile = user.voter_profile
#             profile.profile_picture = voter.profile_picture
#             profile.bio = voter.bio
#             profile.county = voter.county
#             profile.constituency = voter.constituency
#             profile.ward = voter.ward
#             profile.save()
            
#             return Response(VoterSerializer(voter).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
