from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

# TODO: Create your routers and urls here
router = SimpleRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework'))
]
