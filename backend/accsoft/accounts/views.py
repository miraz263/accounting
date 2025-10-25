from rest_framework import viewsets, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Account, JournalEntry, JournalLine
from .serializers import AccountSerializer, JournalEntrySerializer, LedgerLineSerializer

# -----------------------------
# Account ViewSet
# -----------------------------
class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']

# -----------------------------
# JournalEntry ViewSet
# -----------------------------
class JournalEntryViewSet(viewsets.ModelViewSet):
    queryset = JournalEntry.objects.prefetch_related('lines').all()
    serializer_class = JournalEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        company = self.request.query_params.get('company')
        if company:
            qs = qs.filter(company_id=company)
        return qs

# -----------------------------
# Ledger API View
# -----------------------------
class LedgerView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # JWT / login required

    def get(self, request, account_id):
        lines = JournalLine.objects.filter(account_id=account_id)\
                                   .select_related('entry')\
                                   .order_by('entry__date')
        serializer = LedgerLineSerializer(lines, many=True)
        return Response(serializer.data)
