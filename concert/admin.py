from django.contrib import admin
from .models import Concert, ConcertAttending


@admin.register(Concert)
class ConcertAdmin(admin.ModelAdmin):
    list_display = ("concert_name", "city", "date", "duration")
    search_fields = ("concert_name", "city")
    list_filter = ("date",)


@admin.register(ConcertAttending)
class ConcertAttendingAdmin(admin.ModelAdmin):
    list_display = ("concert", "user", "attending")
    list_filter = ("attending",)
