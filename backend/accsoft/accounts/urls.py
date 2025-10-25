from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, JournalEntryViewSet, LedgerView

router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'journal-entries', JournalEntryViewSet)

urlpatterns = [
    path('', include(router.urls)),  # ViewSets API
    path('ledger/<int:account_id>/', LedgerView.as_view(), name='ledger-view'),  # Ledger API
]
