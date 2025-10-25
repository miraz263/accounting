from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import Account, JournalLine
from django.db.models import Sum, F

class TrialBalanceView(APIView):
    def get(self, request):
        company_id = request.query_params.get('company')
        # aggregate debit & credit per account
        qs = JournalLine.objects.filter(entry__company_id=company_id).values(
            account_id=F('account__id'),
            account_name=F('account__name'),
            account_code=F('account__code'),
        ).annotate(total_debit=Sum('debit'), total_credit=Sum('credit')).order_by('account_code')
        return Response(list(qs))
