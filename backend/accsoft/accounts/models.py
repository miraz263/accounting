from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Company(models.Model):
    name = models.CharField(max_length=255)
    currency = models.CharField(max_length=10, default="BDT")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Account(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='accounts')
    code = models.CharField(max_length=64)  # e.g., 1001
    name = models.CharField(max_length=255)
    TYPE_CHOICES = [
        ('asset','Asset'),
        ('liability','Liability'),
        ('equity','Equity'),
        ('income','Income'),
        ('expense','Expense'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('company','code')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

class JournalEntry(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='entries')
    date = models.DateField()
    narration = models.TextField(blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    # optional: posted boolean
    posted = models.BooleanField(default=True)

    def __str__(self):
        return f"JE-{self.id} {self.date}"

class JournalLine(models.Model):
    entry = models.ForeignKey(JournalEntry, related_name='lines', on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    debit = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['account']),
            models.Index(fields=['entry','account']),
        ]
