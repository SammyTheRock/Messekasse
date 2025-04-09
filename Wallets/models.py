from django.db import models
from django.conf import settings
from django.utils import timezone
from Users.models import User


# ===========================
# Wallet Model
# ===========================
class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True)
    sum = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Wallet of {self.user.name} – {self.sum} €"

# ===========================
# Wallet Activity Model
# ===========================
class WalletActivity(models.Model):
    class ActivityType(models.TextChoices):
        DEBIT = 'Debit', 'Debit'
        DEPOSIT = 'Deposit', 'Deposit'

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='activities')
    basket = models.TextField(blank=True)  # Optional: Details über gekaufte Artikel
    datetime = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True)
    activity_type = models.CharField(max_length=10, choices=ActivityType.choices)
    beleg_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    

    def __str__(self):
        return f"{self.activity_type} {self.amount} € for {self.wallet.user.name} on {self.datetime}"

