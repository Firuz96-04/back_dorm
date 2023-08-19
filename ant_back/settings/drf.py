

CORS_ALLOW_ALL_ORIGINS = True

# CORS_ALLOWED_ORIGINS = [
# "https://domain.com",
# "https://api.domain.com",
# "http://localhost:3000",
# "http://127.0.0.1:9000"
# ]

CORS_ALLOWED_HEADERS = [
    'Accept',
    'Authorization',
    'Content-Type',
]
REST_FRAMEWORK = {
    # 'DEFAULT_RENDERER_CLASSES': [
    #     'rest_framework.renderers.JSONRenderer',
    #     'rest_framework.parsers.FormParser',
    #     'rest_framework.parsers.MultiPartParser'
    # ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
#
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}


