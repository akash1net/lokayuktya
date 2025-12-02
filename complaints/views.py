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
        print("akash sharma",request.data)
        return super().create(request, *args, **kwargs)
    
    

    # @swagger_auto_schema(
    #     method="post",
    #     request_body=EvidenceUploadSerializer,
    #     responses={
    #         200: openapi.Response(
    #             description="Evidence uploaded successfully"
    #         )
    #     }
    # )
    # @action(detail=False, methods=["POST"], url_path="upload-evidence")
    # def upload_evidence(self, request):
    #     try:
    #         serializer = EvidenceUploadSerializer(data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         evidence = serializer.save()

    #         return Response({
    #             "message": "Uploaded",
    #             "evidence_id": evidence.id,
    #             "file_url": request.build_absolute_uri(evidence.evidence_file.url)
    #         })

    #     except Exception as e:
    #         return Response({"error": str(e)}, status=400)
        
        
   

        

        


class EvidenceViewSet(viewsets.GenericViewSet):
    queryset = EvidenceDocument.objects.all()
    serializer_class = EvidenceUploadSerializer
    parser_classes = [MultiPartParser, FormParser]

    # ----------------------
    # 1️⃣ UPLOAD EVIDENCE
    # ----------------------
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
        try:
            serializer = EvidenceUploadSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            evidence = serializer.save()

            return Response({
                "message": "Uploaded",
                "evidence_id": evidence.id,
                "file_url": request.build_absolute_uri(evidence.evidence_file.url)
            })

        except Exception as e:
            return Response({"error": str(e)}, status=400)

    # ----------------------
    # 2️⃣ DELETE EVIDENCE
    # ----------------------
    @swagger_auto_schema(
        method="delete",
        responses={200: "Evidence deleted successfully"}
    )
    @action(detail=True, methods=['delete'], url_path='')
    def delete(self, request, pk=None):
        """Delete evidence by ID (pk = evidence_id)"""

        try:
            evidence = self.get_object()
        except:
            return Response({"error": "Evidence not found"}, status=404)

        evidence.delete()
        return Response({"message": "Deleted successfully"}, status=200)


 
    



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
    



class FollowUpDocumentViewSet(viewsets.GenericViewSet):
    queryset = FollowUpDocument.objects.all()
    serializer_class = FollowUpUploadSerializer
    parser_classes = [MultiPartParser, FormParser]

    # ------------------------------
    # UPLOAD FOLLOW-UP DOCUMENT
    # ------------------------------
    @swagger_auto_schema(
        method="post",
        request_body=FollowUpUploadSerializer,
        responses={
            200: openapi.Response(description="Follow-up document uploaded successfully")
        }
    )
    @action(detail=False, methods=["POST"], url_path="upload")
    def upload_document(self, request):
        try:
            serializer = FollowUpUploadSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            document = serializer.save()

            return Response({
                "message": "Uploaded successfully",
                "document_id": document.id,
                "file_type": document.file_type,
                "file_url": request.build_absolute_uri(document.evidence_file.url)
            }, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=400)

    # ------------------------------
    # DELETE FOLLOW-UP DOCUMENT
    # ------------------------------
    @swagger_auto_schema(
        method="delete",
        responses={200: "Document deleted successfully"}
    )
    @action(detail=True, methods=['delete'], url_path='')
    def delete_document(self, request, pk=None):
        """Delete follow-up document by ID (pk=document_id)"""

        try:
            document = self.get_object()
        except:
            return Response({"error": "Document not found"}, status=404)

        document.delete()
        return Response({"message": "Deleted successfully"}, status=200)
    




class ComplaintFollowUpViewSet(viewsets.GenericViewSet):
    serializer_class = FollowUpLinkSerializer

    @swagger_auto_schema(
        method="post",
        request_body=FollowUpLinkSerializer,
        responses={200: "Follow-up added successfully"}
    )
    @action(detail=False, methods=['post'], url_path='add-followup')
    def add_followup(self, request):
        serializer = FollowUpLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response({
            "message": "Follow-up added successfully",
            "note_id": data["note_id"],
            "attached_document_ids": data["attached_documents"]
        }, status=200)




class ComplaintTrackingView(viewsets.GenericViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintTrackingSerializer

    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter(
                'complaint_no',
                openapi.IN_QUERY,
                description="Enter Complaint Number",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: "Complaint Full Details"}
    )
    @action(detail=False, methods=["GET"], url_path="track")
    def track_complaint(self, request):
        complaint_no = request.GET.get("complaint_no")

        if not complaint_no:
            return Response({"error": "complaint_no is required"}, status=400)

        try:
            complaint = Complaint.objects.get(complaint_no=complaint_no)
        except Complaint.DoesNotExist:
            return Response({"error": "Complaint not found"}, status=404)

        serializer = ComplaintTrackingSerializer(complaint, context={"request": request})
        return Response(serializer.data, status=200)





