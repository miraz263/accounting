from rest_framework import serializers
from django.db import transaction
from .models import Company, Account, JournalEntry, JournalLine


# ------------------------------
# Account Serializer
# ------------------------------
class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'company', 'code', 'name', 'type', 'parent', 'is_active']


# ------------------------------
# Journal Line Serializer
# ------------------------------
class JournalLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalLine
        fields = ['account', 'debit', 'credit', 'description']


# ------------------------------
# Journal Entry Serializer
# ------------------------------
class JournalEntrySerializer(serializers.ModelSerializer):
    lines = JournalLineSerializer(many=True)

    class Meta:
        model = JournalEntry
        fields = ['id', 'company', 'date', 'narration', 'created_by', 'posted', 'lines']
        read_only_fields = ['created_by']

    def validate(self, data):
        lines = data.get('lines', [])
        total_debit = sum([line.get('debit', 0) or 0 for line in lines])
        total_credit = sum([line.get('credit', 0) or 0 for line in lines])

        if total_debit != total_credit:
            raise serializers.ValidationError("Total debit and credit must be equal.")
        if total_debit == 0 and total_credit == 0:
            raise serializers.ValidationError("Entry cannot be zero.")

        return data

    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        user = self.context['request'].user
        validated_data['created_by'] = user

        with transaction.atomic():
            entry = JournalEntry.objects.create(**validated_data)
            for line in lines_data:
                JournalLine.objects.create(entry=entry, **line)
        return entry


# ------------------------------
# Ledger Line Serializer
# ------------------------------
class LedgerLineSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source='entry.date', read_only=True)
    entry_id = serializers.IntegerField(source='entry.id', read_only=True)
    narration = serializers.CharField(source='entry.narration', read_only=True)

    class Meta:
        model = JournalLine
        fields = ['entry_id', 'date', 'debit', 'credit', 'narration']
