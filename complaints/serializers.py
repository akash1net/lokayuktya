from rest_framework import serializers
from .models import *
import mimetypes
import json
import mimetypes
from rest_framework import serializers
from .models import Respondent, Complaint, ComplaintDocument, EvidenceDocument, PublicFunctionary


class PublicFunctionarySerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicFunctionary
        fields = ('id', 'functionari_name')


class ComplaintCapacitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintCapacity
        fields = ('id','name')


class DocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documents
        fields = ('id', 'name', 'document_type', 'document_file')

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ('id', 'name')

class PublicServientSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicServient
        fields = ('id', 'name', 'designation')


class RespondentSerializer(serializers.ModelSerializer):
    respondent_designation = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(),
        required=False,
        allow_null=True
    )
    public_servient_name = serializers.PrimaryKeyRelatedField(
        queryset=PublicServient.objects.all(),
        required=False,
        allow_null=True
    )
    class Meta:
        model = Respondent
        fields = ['name', 'designation', 'respondent_designation', 'public_servient_name', 'department', 'address']



class ComplaintDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintDocument
        fields = ['document_type', 'document_number', 'document_image']

    def validate(self, data):
        if not data.get('document_number'):
            raise serializers.ValidationError({"document_number": "Document number is required."})
        if not data.get('document_image'):
            raise serializers.ValidationError({"document_image": "Document image is required."})
        return data


class EvidenceDocumentSerializer(serializers.ModelSerializer):
    file_type = serializers.CharField(read_only=True)

    class Meta:
        model = EvidenceDocument
        fields = ['evidence_file', 'description', 'file_type']

    def validate(self, data):
        if not data.get('evidence_file'):
            raise serializers.ValidationError({"evidence_file": "Evidence file is required."})
        return data

    def create(self, validated_data):
        evidence_file = validated_data.get('evidence_file')
        if evidence_file:
            mime_type, _ = mimetypes.guess_type(evidence_file.name)
            if mime_type:
                if mime_type.startswith('image'):
                    validated_data['file_type'] = 'image'
                elif mime_type.startswith('video'):
                    validated_data['file_type'] = 'video'
                elif mime_type.startswith('audio'):
                    validated_data['file_type'] = 'audio'
                elif mime_type == 'application/pdf':
                    validated_data['file_type'] = 'pdf'
                else:
                    validated_data['file_type'] = 'other'
        return super().create(validated_data)


class EvidenceUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceDocument
        fields = ["id", "evidence_file", "description"]


# class EvidenceUploadSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = EvidenceDocument
#         fields = ["id", "evidence_file", "description"]
#         extra_kwargs = {
#             "id": {"read_only": True}
#         }





# class ComplaintSerializer(serializers.ModelSerializer):
#     respondent = RespondentSerializer(required=False)
#     # documents = serializers.JSONField(required=False, write_only=True)
#     evidences = serializers.JSONField(required=False, write_only=True)
#     public_functionaries = serializers.SerializerMethodField()

#     class Meta:
#         model = Complaint
#         fields = [
#             'id', 'complaint_no', 'user', 'complaint_capacity', 'nationality','is_public_functionaries', 'post_name',
#             'public_functionaries', 'complaint_text', 'status', 'respondent',
#             'declaration_accepted', 'signature','affidavit', 'is_fee_verified', 'verify_mob',
#             'confirm_accepted', 'evidences', 'created_at'
#         ]
#         read_only_fields = ['complaint_no', 'created_at']

#     # Return list of IDs for GET API
#     def get_public_functionaries(self, obj):
#         return [pf.id for pf in obj.public_functionaries.all()]

#     # Correct parsing public_functionaries
#     def to_internal_value(self, data):
#         data = super().to_internal_value(data)
#         request = self.context.get('request')
#         pf_raw = request.data.get('public_functionaries')

#         if pf_raw:
#             if isinstance(pf_raw, list):
#                 data['public_functionaries'] = [int(x) for x in pf_raw]
#             elif isinstance(pf_raw, str):
#                 try:
#                     data['public_functionaries'] = json.loads(pf_raw)
#                 except:
#                     data['public_functionaries'] = [
#                         int(x)
#                         for x in pf_raw.replace('[', '').replace(']', '').split(',')
#                         if x.strip()
#                     ]
#         return data

#     def create(self, validated_data):
#         request = self.context.get('request')

#         # ---------------------------
#         # Parse respondent JSON
#         # ---------------------------
#         respondent_raw = request.data.get('respondent')
#         respondent_data = None

#         if respondent_raw:
#             try:
#                 respondent_data = json.loads(respondent_raw)
#             except:
#                 respondent_data = respondent_raw

#         # docs_data = validated_data.pop('documents', [])
#         evid_data = validated_data.pop('evidences', [])
#         public_functionaries_ids = validated_data.pop('public_functionaries', [])

#         # ---------------------------
#         # Create Respondent
#         # ---------------------------
#         respondent = None
#         if respondent_data:
#             respondent_serializer = RespondentSerializer(data=respondent_data)
#             respondent_serializer.is_valid(raise_exception=True)
#             respondent = respondent_serializer.save()
#             validated_data['respondent'] = respondent

#         # ---------------------------
#         # Create Complaint
#         # ---------------------------
#         complaint = Complaint.objects.create(**validated_data)

#         # ---------------------------
#         # Set Public Functionaries (M2M)
#         # ---------------------------
#         if public_functionaries_ids:
#             selected_pfs = PublicFunctionary.objects.filter(id__in=public_functionaries_ids)
#             complaint.public_functionaries.set(selected_pfs)

#         # ---------------------------
#         # Documents (multiple upload)
#         # ---------------------------
#         # if isinstance(docs_data, list):
#         #     for i, doc in enumerate(docs_data):
#         #         file_key = f"documents[{i}][document_image]"
#         #         document_image = request.FILES.get(file_key)

#         #         document_type_id = doc.get('document_type')
#         #         document_type_obj = None
                
#         #         if document_type_id:
#         #             try:
#         #                 document_type_obj = Documents.objects.get(id=document_type_id)
#         #             except Documents.DoesNotExist:
#         #                 raise serializers.ValidationError({
#         #                     "documents": f"Invalid document_type ID {document_type_id}"
#         #                 })

#         #         ComplaintDocument.objects.create(
#         #             complaint=complaint,
#         #             document_type=document_type_obj,
#         #             document_number=doc.get('document_number'),
#         #             document_image=document_image if document_image else None
#         #         )

#         # ---------------------------
#         # Evidences (multiple upload)
#         # ---------------------------
#         if isinstance(evid_data, list):
#             for i, ev in enumerate(evid_data):
#                 file_key = f"evidences[{i}][evidence_file]"
#                 evidence_file = request.FILES.get(file_key)

#                 EvidenceDocument.objects.create(
#                     complaint=complaint,
#                     description=ev.get('description'),
#                     evidence_file=evidence_file if evidence_file else None
#                 )

#         return complaint
    




class ComplaintSerializer(serializers.ModelSerializer):
    respondent = RespondentSerializer(required=False)
    public_functionaries = serializers.SerializerMethodField()
    evidence_ids = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = Complaint
        fields = [
            'id',
            'complaint_no',
            'user',
            'complaint_capacity',
            'nationality',
            'is_public_functionaries',
            'post_name',
            'public_functionaries',
            'complaint_text',
            'status',
            'respondent',
            'declaration_accepted',
            'signature',
            'affidavit',
            'is_fee_verified',
            'is_affidavit',
            'confirm_accepted',
            'evidence_ids',
            'created_at'
        ]
        read_only_fields = ['complaint_no', 'created_at']

    # ------------------------------
    # GET → Public Functionary IDs
    # ------------------------------
    def get_public_functionaries(self, obj):
        return [pf.id for pf in obj.public_functionaries.all()]

    # ------------------------------
    # PARSE BOTH:
    # - public_functionaries
    # - evidence_ids
    # ------------------------------
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        request = self.context.get("request")
        print("print@@@@@@@@@@@@@@@@@@@@",request)

        # ==========================
        # HANDLE evidence_ids
        # ==========================
        raw_evidence = request.data.get("evidence_ids")
        evidence_ids = []

        if raw_evidence:
            if isinstance(raw_evidence, list):
                evidence_ids = [int(x) for x in raw_evidence]

            elif isinstance(raw_evidence, str) and raw_evidence.startswith("["):
                try:
                    evidence_ids = json.loads(raw_evidence)
                except:
                    pass

            else:
                evidence_ids = [
                    int(x)
                    for x in raw_evidence.replace("[", "").replace("]", "").split(",")
                    if x.strip()
                ]

        data["evidence_ids"] = evidence_ids

        # ==========================
        # HANDLE public_functionaries
        # ==========================
        pf_raw = request.data.get("public_functionaries")
        pf_ids = []

        if pf_raw:
            if isinstance(pf_raw, list):
                pf_ids = [int(x) for x in pf_raw]

            elif isinstance(pf_raw, str) and pf_raw.startswith("["):
                pf_ids = json.loads(pf_raw)

            else:
                pf_ids = [
                    int(x)
                    for x in pf_raw.replace("[", "").replace("]", "").split(",")
                    if x.strip()
                ]

        data["public_functionaries"] = pf_ids

        return data

    # ------------------------------
    # CREATE Complaint
    # ------------------------------
    def create(self, validated_data):
        request = self.context.get('request')

        evidence_ids = validated_data.pop("evidence_ids", [])
        public_functionaries_ids = validated_data.pop("public_functionaries", [])

        # Respondent
        respondent_raw = request.data.get('respondent')
        respondent = None

        if respondent_raw:
            try:
                respondent_data = json.loads(respondent_raw)
            except:
                respondent_data = respondent_raw

            rser = RespondentSerializer(data=respondent_data)
            rser.is_valid(raise_exception=True)
            respondent = rser.save()
            validated_data['respondent'] = respondent

        # Create Complaint
        complaint = Complaint.objects.create(**validated_data)

        # Set public functionaries
        if public_functionaries_ids:
            complaint.public_functionaries.set(
                PublicFunctionary.objects.filter(id__in=public_functionaries_ids)
            )

        # Link evidence IDs to complaint
        if evidence_ids:
            EvidenceDocument.objects.filter(id__in=evidence_ids).update(complaint=complaint)

        return complaint





class FollowUpUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUpDocument
        fields = ["id", "evidence_file",]



class FollowUpNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUpNote
        fields = ["id", "description"]




class FollowUpLinkSerializer(serializers.Serializer):
    complaint = serializers.IntegerField()
    description = serializers.CharField(allow_blank=True, required=False)
    document_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )

    def create(self, validated_data):
        complaint_id = validated_data["complaint"]
        description = validated_data.get("description", "")
        document_ids = validated_data.get("document_ids", [])

        # Create Follow-up Note
        note = FollowUpNote.objects.create(
            complaint_id=complaint_id,
            description=description
        )

        #  Attach uploaded follow-up documents
        if document_ids:
            FollowUpDocument.objects.filter(
                id__in=document_ids
            ).update(complaint_id=complaint_id)

        return {
            "note_id": note.id,
            "attached_documents": document_ids
        }



###################################################### Complent Tracking ####################################################
class ComplaintDocumentListSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ComplaintDocument
        fields = ["id", "document_type", "document_number", "file_url"]

    def get_file_url(self, obj):
        if obj.document_image:
            return self.context['request'].build_absolute_uri(obj.document_image.url)
        return None
    

class EvidenceListSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = EvidenceDocument
        fields = ["id", "description", "file_type", "file_url"]

    def get_file_url(self, obj):
        if obj.evidence_file:
            return self.context['request'].build_absolute_uri(obj.evidence_file.url)
        return None
    

class FollowUpDocListSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = FollowUpDocument
        fields = ["id", "file_type", "file_url"]

    def get_file_url(self, obj):
        if obj.evidence_file:
            return self.context['request'].build_absolute_uri(obj.evidence_file.url)
        return None
    

class FollowUpNoteDetailSerializer(serializers.ModelSerializer):
    documents = FollowUpDocListSerializer(source='complaint.followup_documents', many=True, read_only=True)

    class Meta:
        model = FollowUpNote
        fields = ["id", "description", "uploaded_at", "documents"]



class FollowUpDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = FollowUpDocument
        fields = ["id", "file_type", "file_url"]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.evidence_file:
            if request:
                return request.build_absolute_uri(obj.evidence_file.url)
            return obj.evidence_file.url
        return None



class ComplaintTrackingSerializer(serializers.ModelSerializer):
    respondent = RespondentSerializer(read_only=True)
    evidences = serializers.SerializerMethodField()
    followup_note = FollowUpNoteDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Complaint
        fields = [
            "id",
            "complaint_no",
            "user",
            "status",
            "complaint_text",
            "respondent",
            "created_at",
            "evidences",
            "followup_note"
        ]

    def get_evidences(self, obj):
        # normal evidences
        evidences = EvidenceListSerializer(
            obj.evidences.all(),
            many=True,
            context=self.context
        ).data

        # follow-up evidences
        followup_docs = FollowUpDocumentSerializer(
            obj.followup_documents.all(),
            many=True,
            context=self.context
        ).data

        return evidences + followup_docs






