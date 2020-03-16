from rest_framework import routers
from authentication import views as myapp_views

router = routers.DefaultRouter()
router.register(r"register", myapp_views.RegistrationViewset)
router.register(r"login", myapp_views.LoginViewset)
