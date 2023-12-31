from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from dormitory.views import LoginApi,CustomTokenRefreshView
    # , CustomRefresh
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('dormitory.urls')),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/', LoginApi.as_view()),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += path("__debug__/", include("debug_toolbar.urls")),
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
