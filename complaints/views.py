from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, mixins, filters
from .models import *
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse, Http404
from rest_framework.decorators import action
import os
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi




class PublicFunctionaryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    List all active Public Functionaries
    """
    queryset = PublicFunctionary.objects.filter(is_active=True).order_by('id')
    serializer_class = PublicFunctionarySerializer


class ComplaintCapacityViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    List all active Complaint Capacities
    """
    queryset = ComplaintCapacity.objects.filter(is_active=True).order_by('id')
    serializer_class = ComplaintCapacitySerializer


# class DocumentsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     """
#     List all active Documents
#     """
#     queryset = Documents.objects.filter(is_active=True).order_by('id')
#     serializer_class = DocumentsSerializer


from drf_yasg.utils import swagger_auto_schema

class ComplaintViewSet(viewsets.GenericViewSet,
                       mixins.CreateModelMixin,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin):
    queryset = Complaint.objects.all().order_by('-id')
    serializer_class = ComplaintSerializer
    parser_classes = [MultiPartParser, FormParser]


    @swagger_auto_schema(auto_schema=None)  # hides in Swagger
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    

    @swagger_auto_schema(
        method="post",
        request_body=EvidenceUploadSerializer,
        responses={
            200: openapi.Response(
                description="Evidence uploaded successfully"
            )
        }
    )
    @action(detail=False, methods=["POST"], url_path="upload-evidence")
    def upload_evidence(self, request):
        serializer = EvidenceUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        evidence = serializer.save()

        return Response({
            "message": "Uploaded",
            "evidence_id": evidence.id,
            "file_url": request.build_absolute_uri(evidence.evidence_file.url)
        })


    



class DesignationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Designation.objects.filter(is_active=True).order_by('name')
    serializer_class = DesignationSerializer


class PublicServientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PublicServient.objects.filter(is_active=True).order_by('name')
    serializer_class = PublicServientSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['designation']          # ?designation=ID
    search_fields = ['name']  


class DocumentsViewSet(viewsets.ModelViewSet):
    queryset = Documents.objects.all()
    serializer_class = DocumentsSerializer

    # Custom route: /documents/download/?type=affidavit
    @action(detail=False, methods=['GET'], url_path='download')
    def download_document(self, request):

        document_type = "Affidavit"  # default

        try:
            document = Documents.objects.get(document_type=document_type)
        except Documents.DoesNotExist:
            raise Http404(f"No document found for type '{document_type}'")

        if not document.document_file:
            raise Http404("File missing in database")

        file_path = document.document_file.path
        if not os.path.exists(file_path):
            raise Http404("File missing on server")

        # Create absolute URL (frontend-friendly)
        download_url = request.build_absolute_uri(document.document_file.url)
        # media_url = document.document_file.url  
        # api_media_url = media_url.replace("/media/", "/api/media/")
        # final_url = request.build_absolute_uri(api_media_url)

        return Response({
            "status": True,
            "message": f"{document_type} download link generated",
            "download_url": download_url
        }, status=200)

