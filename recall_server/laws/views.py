from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Q
from django.utils import timezone

from recall_server.laws.models import (
    Bill, 
    House, 
    Comment, 
    BillRevision, 
    BillAmendment, 
    PublishedLaw
)
from recall_server.laws.serializers import(
        BillSerializer,
        BillDetailSerializer,
        HouseSerializer,
        CommentSerializer,
        CommentDetailSerializer,
        BillRevisionSerializer,
        BillRevisionDetailSerializer,
        BillAmendmentSerializer,
        PublishedLawSerializer,
        PublishedLawDetailSerializer
)
from recall_server.county.models import County
from recall_server.county.serializers import CountySerializer


class BillPagination(PageNumberPagination):
    """
    Custom pagination for bills with configurable page size.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['title', 'description', 'bill_number', 'tags']
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = BillPagination
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BillDetailSerializer
        return BillSerializer

    def get_queryset(self):
        queryset = self.queryset
        house = self.request.query_params.get('house')
        county = self.request.query_params.get('county')
        status = self.request.query_params.get('status')
        stage = self.request.query_params.get('stage')
        tags = self.request.query_params.get('tags')
        proposer_type = self.request.query_params.get('proposer_type')
        
        # Filter by house
        if house:
            queryset = queryset.filter(house__name=house)

        # Filter by county for county assembly bills
        if house == 'county_assembly' and county:
            queryset = queryset.filter(county__name=county)
            
        # Filter by status
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by stage
        if stage:
            queryset = queryset.filter(stage=stage)
            
        # Filter by tags
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            q_objects = Q()
            for tag in tag_list:
                q_objects |= Q(tags__icontains=tag)
            queryset = queryset.filter(q_objects)
            
        # Filter by proposer type
        if proposer_type:
            if proposer_type == 'mp':
                queryset = queryset.filter(proposed_by_mp__isnull=False)
            elif proposer_type == 'senator':
                queryset = queryset.filter(proposed_by_senator__isnull=False)
            elif proposer_type == 'mca':
                queryset = queryset.filter(proposed_by_mca__isnull=False)

        return queryset

    @action(detail=False, methods=['get'])
    def houses(self, request):
        """
        Returns a list of houses i.e Senate, Parliament, County
        """
        houses = House.objects.all()
        serializer = HouseSerializer(houses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def counties(self, request):
        """
        Returns a list of counties when County is selected
        """
        house = request.query_params.get('house')
        if house == 'county_assembly':
            counties = County.objects.all()
            serializer = CountySerializer(counties, many=True)
            return Response(serializer.data)
        return Response({"detail": "County data currently unavailable"})

    @action(detail=False, methods=['get'])
    def bills_by_county(self, request):
        """
        Returns a list of bills by county
        """
        county = request.query_params.get('county')
        if county:
            bills = self.get_queryset().filter(county__name=county)
            serializer = BillSerializer(bills, many=True)
            return Response(serializer.data)
        return Response({"detail": "No county provided."})
        
    @action(detail=False, methods=['get'])
    def active_bills(self, request):
        """
        Returns a list of currently active bills that can be voted on
        """
        now = timezone.now()
        bills = self.get_queryset().filter(
            status='active',
            deadline_for_voting__gt=now
        )
        serializer = BillSerializer(bills, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def popular_bills(self, request):
        """
        Returns a list of bills with the most public votes and comments
        """
        bills = self.get_queryset().annotate(
            total_votes=Count('public_votes'),
            total_comments=Count('discussions')
        ).order_by('-total_votes', '-total_comments')[:10]
        
        serializer = BillSerializer(bills, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['post'])
    def update_stage(self, request, pk=None):
        """
        Update the stage of a bill
        """
        bill = self.get_object()
        new_stage = request.data.get('stage')
        notes = request.data.get('notes', '')
        
        if not new_stage:
            return Response({"detail": "No stage provided."}, status=status.HTTP_400_BAD_REQUEST)
            
        bill.update_stage(new_stage, notes)
        return Response({"detail": f"Bill stage updated to {new_stage}"})
        
    @action(detail=True, methods=['get'])
    def vote_comparison(self, request, pk=None):
        """
        Compare public opinion with official votes
        """
        bill = self.get_object()
        bill.update_vote_counts()
        
        public_opinion = bill.get_public_opinion_percentage()
        official_votes = bill.get_official_vote_percentage()
        
        # Calculate alignment
        alignment = 0
        if public_opinion['yes'] > 0 and official_votes['yes'] > 0:
            alignment = min(public_opinion['yes'], official_votes['yes'])
            
        if public_opinion['no'] > 0 and official_votes['no'] > 0:
            alignment += min(public_opinion['no'], official_votes['no'])
            
        if public_opinion['abstain'] > 0 and official_votes['abstain'] > 0:
            alignment += min(public_opinion['abstain'], official_votes['abstain'])
            
        return Response({
            'public_opinion': public_opinion,
            'official_votes': official_votes,
            'alignment_percentage': alignment
        })
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        """
        Follow a bill to receive updates
        """
        bill = self.get_object()
        user = request.user
        
        if hasattr(user, 'followed_bills'):
            user.followed_bills.add(bill)
            return Response({"detail": "You are now following this bill."})
        return Response({"detail": "Unable to follow bill."}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk=None):
        """
        Unfollow a bill
        """
        bill = self.get_object()
        user = request.user
        
        if hasattr(user, 'followed_bills'):
            user.followed_bills.remove(bill)
            return Response({"detail": "You have unfollowed this bill."})
        return Response({"detail": "Unable to unfollow bill."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Advanced search for bills with multiple parameters and full-text search
        """
        query = request.query_params.get('q', '')
        house = request.query_params.get('house')
        status = request.query_params.get('status')
        stage = request.query_params.get('stage')
        tags = request.query_params.get('tags')
        proposer_type = request.query_params.get('proposer_type')
        proposer_id = request.query_params.get('proposer_id')
        county = request.query_params.get('county')
        constituency = request.query_params.get('constituency')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        sort_by = request.query_params.get('sort_by', 'created_at')
        sort_order = request.query_params.get('sort_order', 'desc')
        
        # Start with all bills
        queryset = self.get_queryset()
        
        # Apply full-text search if query is provided
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(summary__icontains=query) |
                Q(bill_number__icontains=query) |
                Q(tags__icontains=query)
            )
            
        # Filter by house
        if house:
            queryset = queryset.filter(house__name=house)
            
        # Filter by status
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by stage
        if stage:
            queryset = queryset.filter(stage=stage)
            
        # Filter by tags
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            q_objects = Q()
            for tag in tag_list:
                q_objects |= Q(tags__icontains=tag)
            queryset = queryset.filter(q_objects)
            
        # Filter by proposer type
        if proposer_type:
            if proposer_type == 'mp':
                queryset = queryset.filter(proposed_by_mp__isnull=False)
                if proposer_id:
                    queryset = queryset.filter(proposed_by_mp__tokenized_id=proposer_id)
            elif proposer_type == 'senator':
                queryset = queryset.filter(proposed_by_senator__isnull=False)
                if proposer_id:
                    queryset = queryset.filter(proposed_by_senator__tokenized_id=proposer_id)
            elif proposer_type == 'mca':
                queryset = queryset.filter(proposed_by_mca__isnull=False)
                if proposer_id:
                    queryset = queryset.filter(proposed_by_mca__tokenized_id=proposer_id)
                    
        # Filter by county
        if county:
            # For county assembly bills
            queryset = queryset.filter(
                Q(house__name='county_assembly', county__name=county) |
                Q(proposed_by_senator__county__name=county) |
                Q(proposed_by_mca__constituency__county__name=county)
            )
            
        # Filter by constituency
        if constituency:
            queryset = queryset.filter(
                Q(proposed_by_mp__constituency=constituency) |
                Q(proposed_by_mca__constituency__name=constituency)
            )
            
        # Filter by date range
        if date_from:
            queryset = queryset.filter(proposed_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(proposed_date__lte=date_to)
            
        # Apply sorting
        if sort_order.lower() == 'asc':
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by(f'-{sort_by}')
            
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def create_revision(self, request, pk=None):
        """
        Create a new revision for this bill
        """
        bill = self.get_object()
        content = request.data.get('content')
        summary = request.data.get('summary', '')
        is_published = request.data.get('is_published', False)
        
        if not content:
            return Response({"detail": "Content is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        revision = bill.create_revision(
            content=content, 
            summary=summary, 
            created_by=request.user,
            is_published=is_published
        )
        
        return Response(BillRevisionSerializer(revision).data)
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def publish_law(self, request, pk=None):
        """
        Publish this bill as an enacted law
        """
        bill = self.get_object()
        law_number = request.data.get('law_number')
        enactment_date = request.data.get('enactment_date')
        effective_date = request.data.get('effective_date')
        gazette_reference = request.data.get('gazette_reference', '')
        
        if not law_number or not enactment_date or not effective_date:
            return Response({
                "detail": "law_number, enactment_date, and effective_date are required."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            law = bill.publish_law(
                law_number=law_number,
                enactment_date=enactment_date,
                effective_date=effective_date,
                gazette_reference=gazette_reference
            )
            return Response(PublishedLawSerializer(law).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def start_public_participation(self, request, pk=None):
        """
        Start the public participation period for this bill
        """
        bill = self.get_object()
        end_date = request.data.get('end_date')
        
        if not end_date:
            return Response({"detail": "End date is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        bill.start_public_participation(end_date)
        
        return Response({"detail": "Public participation started."})
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def end_public_participation(self, request, pk=None):
        """
        End the public participation period for this bill
        """
        bill = self.get_object()
        bill.end_public_participation()
        
        return Response({"detail": "Public participation ended."})
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def refer_to_committee(self, request, pk=None):
        """
        Refer this bill to a committee
        """
        bill = self.get_object()
        committee_name = request.data.get('committee')
        
        if not committee_name:
            return Response({"detail": "Committee name is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        bill.refer_to_committee(committee_name)
        
        return Response({"detail": f"Bill referred to {committee_name}."})
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_committee_report(self, request, pk=None):
        """
        Add a committee report to this bill
        """
        bill = self.get_object()
        report = request.data.get('report')
        recommendation = request.data.get('recommendation')
        
        if not report or not recommendation:
            return Response({
                "detail": "Report and recommendation are required."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        bill.add_committee_report(report, recommendation)
        
        return Response({"detail": "Committee report added."})
        
    @action(detail=True, methods=['get'])
    def revisions(self, request, pk=None):
        """
        Get all revisions for this bill
        """
        bill = self.get_object()
        revisions = bill.revisions.all()
        
        # Filter by published status if requested
        published = request.query_params.get('published')
        if published is not None:
            is_published = published.lower() == 'true'
            revisions = revisions.filter(is_published=is_published)
            
        serializer = BillRevisionSerializer(revisions, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['get'])
    def amendments(self, request, pk=None):
        """
        Get all amendments for this bill
        """
        bill = self.get_object()
        amendments = bill.amendments.all()
        
        # Filter by status if requested
        status_param = request.query_params.get('status')
        if status_param:
            amendments = amendments.filter(status=status_param)
            
        serializer = BillAmendmentSerializer(amendments, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'likes_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CommentDetailSerializer
        return CommentSerializer
    
    def get_queryset(self):
        queryset = self.queryset
        bill_id = self.request.query_params.get('bill')
        featured = self.request.query_params.get('featured')
        parent = self.request.query_params.get('parent')
        
        if bill_id:
            queryset = queryset.filter(bill_id=bill_id)
            
        if featured:
            queryset = queryset.filter(is_featured=True)
            
        if parent:
            if parent == 'none':
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent)
                
        return queryset.filter(is_approved=True)
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """
        Like a comment
        """
        comment = self.get_object()
        comment.like()
        return Response({"detail": "Comment liked successfully."})
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def report(self, request, pk=None):
        """
        Report a comment for moderation
        """
        comment = self.get_object()
        comment.report()
        return Response({"detail": "Comment reported successfully."})


class BillRevisionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for the BillRevision model.
    """
    queryset = BillRevision.objects.all()
    serializer_class = BillRevisionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BillRevisionDetailSerializer
        return BillRevisionSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by bill if requested
        bill_id = self.request.query_params.get('bill')
        if bill_id:
            queryset = queryset.filter(bill_id=bill_id)
            
        # Filter by published status if requested
        published = self.request.query_params.get('published')
        if published is not None:
            is_published = published.lower() == 'true'
            queryset = queryset.filter(is_published=is_published)
            
        return queryset
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def publish(self, request, pk=None):
        """
        Mark a revision as published
        """
        revision = self.get_object()
        revision.is_published = True
        revision.save()
        
        return Response({"detail": "Revision published."})
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unpublish(self, request, pk=None):
        """
        Mark a revision as unpublished
        """
        revision = self.get_object()
        revision.is_published = False
        revision.save()
        
        return Response({"detail": "Revision unpublished."})


class BillAmendmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for the BillAmendment model.
    """
    queryset = BillAmendment.objects.all()
    serializer_class = BillAmendmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by bill if requested
        bill_id = self.request.query_params.get('bill')
        if bill_id:
            queryset = queryset.filter(bill_id=bill_id)
            
        # Filter by status if requested
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        # Filter by proposer if requested
        proposer_id = self.request.query_params.get('proposer')
        if proposer_id:
            queryset = queryset.filter(
                Q(proposed_by_id=proposer_id) |
                Q(proposed_by_mp_id=proposer_id) |
                Q(proposed_by_senator_id=proposer_id) |
                Q(proposed_by_mca_id=proposer_id)
            )
            
        return queryset
        
    def perform_create(self, serializer):
        serializer.save(proposed_by=self.request.user)
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """
        Approve an amendment
        """
        amendment = self.get_object()
        revision_id = request.data.get('revision_id')
        
        if not revision_id:
            return Response({"detail": "Revision ID is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            revision = BillRevision.objects.get(revision_id=revision_id)
            
            # Update the amendment
            amendment.status = 'approved'
            amendment.incorporated_in = revision
            amendment.save()
            
            return Response({"detail": "Amendment approved."})
        except BillRevision.DoesNotExist:
            return Response({"detail": "Revision not found."}, status=status.HTTP_404_NOT_FOUND)
            
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        """
        Reject an amendment
        """
        amendment = self.get_object()
        amendment.status = 'rejected'
        amendment.save()
        
        return Response({"detail": "Amendment rejected."})
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def withdraw(self, request, pk=None):
        """
        Withdraw an amendment
        """
        amendment = self.get_object()
        
        # Only the proposer can withdraw
        if amendment.proposed_by != request.user:
            return Response({"detail": "Only the proposer can withdraw."}, status=status.HTTP_403_FORBIDDEN)
            
        amendment.status = 'withdrawn'
        amendment.save()
        
        return Response({"detail": "Amendment withdrawn."})


class PublishedLawViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for the PublishedLaw model.
    PublishedLaws are read-only as they represent enacted legislation.
    """
    queryset = PublishedLaw.objects.all()
    serializer_class = PublishedLawSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PublishedLawDetailSerializer
        return PublishedLawSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by bill if requested
        bill_id = self.request.query_params.get('bill')
        if bill_id:
            queryset = queryset.filter(bill_id=bill_id)
            
        # Filter by enactment date range
        enactment_from = self.request.query_params.get('enactment_from')
        if enactment_from:
            queryset = queryset.filter(enactment_date__gte=enactment_from)
            
        enactment_to = self.request.query_params.get('enactment_to')
        if enactment_to:
            queryset = queryset.filter(enactment_date__lte=enactment_to)
            
        # Filter by effective date range
        effective_from = self.request.query_params.get('effective_from')
        if effective_from:
            queryset = queryset.filter(effective_date__gte=effective_from)
            
        effective_to = self.request.query_params.get('effective_to')
        if effective_to:
            queryset = queryset.filter(effective_date__lte=effective_to)
            
        # Search by law number or title
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(law_number__icontains=search) |
                Q(title__icontains=search) |
                Q(gazette_reference__icontains=search)
            )
            
        return queryset
