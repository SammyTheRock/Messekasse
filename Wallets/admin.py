from django.contrib import admin
from Wallets.models import Wallet,WalletActivity

# Register your models here.
admin.site.register(Wallet)
admin.site.register(WalletActivity)