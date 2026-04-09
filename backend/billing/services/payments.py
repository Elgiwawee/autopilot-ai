# billing/services/payments.py

from django.utils import timezone
from billing.models import Payment, Invoice

from billing.services.payouts import settle_revenue_share

def mark_invoice_paid(invoice: Invoice, provider_ref: str):

    payment = Payment.objects.get(invoice=invoice)

    payment.status = "PAID"
    payment.provider_reference = provider_ref
    payment.paid_at = timezone.now()
    payment.save()

    invoice.status = "PAID"
    invoice.paid_at = payment.paid_at
    invoice.save(update_fields=["status", "paid_at"])

    # 🔥 ADD THIS
    settle_revenue_share(invoice)