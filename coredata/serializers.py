from rest_framework import serializers
from .models import *


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = [
            "id",
            "title",
            "link",
            "is_clickable",
            "platform_type",
            "is_active",
            "image",  # explicitly add image
        ]






class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ["id","title", "description", "image", "is_active"]




class HighlightsSerializer(serializers.ModelSerializer):
    highlight_date = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    class Meta:
        model = Highlights
        fields = ["id","title", "description", "image", "is_active", "highlight_date"]


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["id","question", "answer", "is_active"]



class LokayuktaProfilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lokayukta
        fields = ["id","title", "description", "image", "is_active", "lokayukta_status", "user_position"]




class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = ['id', 'page_type', 'title', 'content', 'image']


class StaticPageSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = ['id', 'page_type']




class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'iso_code', 'phone_code', 'is_active']



class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name', 'code', 'country', 'is_active']




