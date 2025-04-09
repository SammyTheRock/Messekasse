from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from Wallets.models import Wallet, WalletActivity
from Articles.models import Article
from Users.models import User


# ===========================
# Basket Model
# ===========================
class Basket(models.Model):
    class BasketState(models.TextChoices):
        OPEN = 'Open', 'Offen'
        PURCHASED = 'Purchased', 'Gekauft'
        CANCELLED = 'Cancelled', 'Abgebrochen'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=timezone.now)
    state = models.CharField(max_length=20, choices=BasketState.choices, default=BasketState.OPEN)
    sum = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def calculate_sum(self):
        total = Decimal("0.00")
        for item in self.bought_articles.all():
            total += item.article.price * item.amount
        self.sum = total
        return total

    def purchase(self):
        if self.state != self.BasketState.OPEN:
            raise ValueError("Only open baskets can be purchased.")

        self.calculate_sum()

        # Nutzer-Wallet abrufen und prüfen
        wallet = Wallet.objects.get(user=self.user)
        if wallet.sum < self.sum:
            raise ValueError("Insufficient funds in user's wallet.")

        # Neue WalletActivity anlegen
        WalletActivity.objects.create(
            wallet=wallet,
            basket=str(self.id),
            datetime=timezone.now(),
            description="Kauf von Artikeln",
            activity_type=WalletActivity.ActivityType.DEBIT,
            beleg_id=f"BASKET-{self.id}",
            amount=self.sum
        )

        self.state = self.BasketState.PURCHASED
        self.save()

    def __str__(self):
        return f"Basket {self.id} – {self.user.user_id} – {self.state}"

# ===========================
# BoughtArticle Model
# ===========================
class BoughtArticle(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name='bought_articles')
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.amount}x {self.article.title} in Basket {self.basket.id}"

