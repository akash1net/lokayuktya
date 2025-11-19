from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.http import FileResponse, Http404
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

class BannerViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Banner.objects.all().order_by('-created_at')
    serializer_class = BannerSerializer
    parser_classes = (MultiPartParser, FormParser)

    #  for full image URLs in serializer
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    #  Grouped list by platform_type
    def list(self, request, *args, **kwargs):
        queryset = Banner.objects.all().order_by('-created_at')
        active = self.request.query_params.get('is_active')

        if active is not None:
            queryset = queryset.filter(is_active=active.lower() == 'true')

        grouped_data = {}
        for platform in ['web', 'app', 'both']:
            banners = queryset.filter(platform_type=platform)
            serializer = self.get_serializer(banners, many=True)
            grouped_data[platform] = serializer.data

        return Response({
            "status": "success",
            "data": grouped_data
        }, status=status.HTTP_200_OK)

    #  Create method (explicit fields)
    def create(self, request, *args, **kwargs):
        data = {
            "title": request.data.get("title"),
            "link": request.data.get("link"),
            "is_clickable": request.data.get("is_clickable"),
            "platform_type": request.data.get("platform_type"),
            "is_active": request.data.get("is_active"),
            "image": request.data.get("image"),
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "status": "success",
            "data": serializer.data,
            "message": "Banner created successfully"
        }, status=status.HTTP_201_CREATED)

    # Update method (explicit fields)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        data = {
            "title": request.data.get("title", instance.title),
            "link": request.data.get("link", instance.link),
            "is_clickable": request.data.get("is_clickable", instance.is_clickable),
            "platform_type": request.data.get("platform_type", instance.platform_type),
            "is_active": request.data.get("is_active", instance.is_active),
            "image": request.data.get("image", instance.image),
        }

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "status": "success",
            "data": serializer.data,
            "message": "Banner updated successfully"
        })


class GalleryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Gallery.objects.all().order_by('-created_at')
    serializer_class = GallerySerializer
    parser_classes = (MultiPartParser, FormParser)

    # Full URL for image
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    # Filter by active
    def get_queryset(self):
        queryset = Gallery.objects.all().order_by('-created_at')
        active = self.request.query_params.get('is_active')
        if active is not None:
            queryset = queryset.filter(is_active=active.lower() == 'true')
        return queryset

    # Explicit create
    def create(self, request, *args, **kwargs):
        data = {
            "title": request.data.get("title"),
            "description": request.data.get("description"),
            "image": request.data.get("image"),
            "is_active": request.data.get("is_active", True),
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "status": "success",
            "data": serializer.data,
            "message": "Gallery image created successfully"
        }, status=status.HTTP_201_CREATED)

    # Explicit update
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = {
            "title": request.data.get("title", instance.title),
            "description": request.data.get("description", instance.description),
            "image": request.data.get("image", instance.image),
            "is_active": request.data.get("is_active", instance.is_active),
        }
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "status": "success",
            "data": serializer.data,
            "message": "Gallery image updated successfully"
        })
    


class FAQViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = FAQ.objects.all().order_by('-id')
    serializer_class = FAQSerializer

    def get_queryset(self):
        queryset = FAQ.objects.all().order_by('-id')
        active = self.request.query_params.get('is_active')
        if active is not None:
            queryset = queryset.filter(is_active=active.lower() == 'true')
        return queryset

    # Create method
    def create(self, request, *args, **kwargs):
        data = {
            "question": request.data.get("question"),
            "answer": request.data.get("answer"),
            "is_active": request.data.get("is_active", True),
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "status": "success",
            "data": serializer.data,
            "message": "FAQ created successfully"
        }, status=status.HTTP_201_CREATED)

    #  Update method
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        data = {
            "question": request.data.get("question", instance.question),
            "answer": request.data.get("answer", instance.answer),
            "is_active": request.data.get("is_active", instance.is_active),
        }

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "status": "success",
            "data": serializer.data,
            "message": "FAQ updated successfully"
        })
    


class HighlightsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Highlights.objects.all().order_by('-created_at')
    serializer_class = HighlightsSerializer
    parser_classes = (MultiPartParser, FormParser)

    # Full image URL
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    # Filter by active
    def get_queryset(self):
        queryset = Highlights.objects.all().order_by('-created_at')
        active = self.request.query_params.get('is_active')
        if active is not None:
            queryset = queryset.filter(is_active=active.lower() == 'true')
        return queryset

    # Explicit create
    def create(self, request, *args, **kwargs):
        data = {
            "title": request.data.get("title"),
            "description": request.data.get("description"),
            "image": request.data.get("image"),
            "highlight_date": request.data.get("highlight_date"),
            "is_active": request.data.get("is_active", True),
            
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "status": "success",
            "data": serializer.data,
            "message": "Highlight created successfully"
        }, status=status.HTTP_201_CREATED)

    # Explicit update
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = {
            "title": request.data.get("title", instance.title),
            "description": request.data.get("description", instance.description),
            "image": request.data.get("image", instance.image),
            "highlight_date": request.data.get("highlight_date", instance.highlight_date), 
            "is_active": request.data.get("is_active", instance.is_active),
            
        }
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "status": "success",
            "data": serializer.data,
            "message": "Highlight updated successfully"
        })

    # ✅ Download endpoint
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        try:
            highlight = self.get_object()
            file_path = highlight.image.path
            response = FileResponse(open(file_path, 'rb'))
            response['Content-Disposition'] = f'attachment; filename="{highlight.image.name.split("/")[-1]}"'
            return response
        except Exception as e:
            raise Http404(f"File not found: {str(e)}")


    


class LokayuktaViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Lokayukta.objects.all().order_by('-created_at')
    serializer_class = LokayuktaProfilesSerializer
    parser_classes = (MultiPartParser, FormParser)

    # Full image URL
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    # Filter by active
    def get_queryset(self):
        queryset = Lokayukta.objects.all().order_by('-created_at')
        active = self.request.query_params.get('is_active')
        if active is not None:
            queryset = queryset.filter(is_active=active.lower() == 'true')
        return queryset

    # Explicit create
    def create(self, request, *args, **kwargs):
        data = {
            "title": request.data.get("title"),
            "description": request.data.get("description"),
            "image": request.data.get("image"),
            "lokayukta_status": request.data.get("lokayukta_status"),
            "user_position": request.data.get("user_position"),
            "is_active": request.data.get("is_active", True),
            
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "status": "success",
            "data": serializer.data,
            "message": "Lokayukta Profiles created successfully"
        }, status=status.HTTP_201_CREATED)


    # Explicit update
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = {
            "title": request.data.get("title"),
            "description": request.data.get("description"),
            "image": request.data.get("image"),
            "lokayukta_status": request.data.get("lokayukta_status"),
            "user_position": request.data.get("user_position"),
            "is_active": request.data.get("is_active", True),
            
        }
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "status": "success",
            "data": serializer.data,
            "message": "Lokayukta Profiles updated successfully"
        })



class StaticPageViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = StaticPage.objects.all()
    serializer_class = StaticPageSerializer
    permission_classes = [AllowAny]
    lookup_field = 'page_type'  # fetch using /about, /terms, etc.


    # Custom endpoint for summary list (id + page_type)
    @action(detail=False, methods=['get'], url_path='summary')
    def summary_list(self, request):
        pages = self.get_queryset()
        serializer = StaticPageSummarySerializer(pages, many=True)
        return Response(serializer.data)
    


class CountryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Country.objects.all().order_by('name')
    serializer_class = CountrySerializer
    

    # Full image URL
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    # Filter by active
    def get_queryset(self):
        queryset = Country.objects.all().order_by('name')
        queryset = queryset.filter(is_active = True)
        return queryset
    



class StateViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = State.objects.all().order_by('name')
    serializer_class = StateSerializer
    

    # Full image URL
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    # Filter by active
    def get_queryset(self):
        queryset = State.objects.all().order_by('name')
        queryset = queryset.filter(is_active = True)
        return queryset
    


    # GET endpoint: /api/states/by-country/?country_id=73
    @action(detail=False, methods=['get'], url_path='by-country')
    def get_states_by_country(self, request):
        country_id = request.query_params.get('country_id')

        if not country_id:
            return Response(
                {"error": "country_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        states = State.objects.filter(country_id=country_id, is_active=True).order_by('name')
        serializer = self.get_serializer(states, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)