from django.contrib import admin
from .models import Data, EnrichmentOutput  # Dataset, Measurement,

# Register your models here.

admin.site.register(Data)
admin.site.register(EnrichmentOutput)
# admin.site.register(Dataset)
# admin.site.register(Measurement)
