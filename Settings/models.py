from django.db import models

class Settings(models.Model):
    paypal_link = models.URLField(verbose_name="PayPal-Link")
    bild_links = models.ImageField(upload_to='settings/', verbose_name="Bild links", blank=True)
    bild_rechts = models.ImageField(upload_to='settings/', verbose_name="Bild rechts", blank=True)
    beschreibung = models.TextField(blank=True, verbose_name="Beschreibung (optional)")

    def __str__(self):
        return f"Settings ({self.id})"

    class Meta:
        verbose_name = "Einstellungen"
        verbose_name_plural = "Einstellungen"
