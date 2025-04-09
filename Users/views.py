# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from .models import User
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from Articles.models import Category, Article
from Baskets.models import Basket, BoughtArticle
from django.utils import timezone
from Wallets.models import Wallet, WalletActivity
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from collections import defaultdict
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from Settings.models import Settings
from django.db.models import Q
import random

@login_required
def nutzer_anlegen(request):
    if not request.user.is_superuser:
        messages.error(request, "Zugriff verweigert.")
        return redirect('home')

    User = get_user_model()

    if request.method == 'POST':
        pin = request.POST.get('pin')
        password = request.POST.get('password')
        name = request.POST.get('name')
        title = request.POST.get('title')
        email = request.POST.get('email')
        barcode = request.POST.get('barcode')
        admin = request.POST.get('admin')
        """
        if not all([user_id, pin, password]):
            messages.error(request, "User-ID, PIN und Passwort sind Pflichtfelder.")
            return redirect('nutzer_anlegen')

        if User.objects.filter(user_id=user_id).exists():
            messages.error(request, "Ein Nutzer mit dieser User-ID existiert bereits.")
            return redirect('nutzer_anlegen')
        """
        # User + Profile anlegen
        user = User.objects.create_user(
            pin=pin, 
            password=password,
            name=name,
            title=title,
            email_address=email,
            barcode=barcode)
      
        messages.success(request, f"Nutzer '{name}' erfolgreich angelegt.")
        return redirect('management')  # oder wo du hin willst

    return render(request, 'nutzer_anlegen.html')

@require_POST
@login_required
def deaktiviere_nutzer(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, "Zugriff verweigert.")
        return redirect('management')

    User = get_user_model()
    user = get_object_or_404(User, user_id=user_id)

    if user.is_active:
        user.is_active = False
        user.save()
        messages.success(request, f"Nutzer {user.user_id} wurde deaktiviert.")
    else:
        messages.info(request, f"Nutzer {user.user_id} ist bereits deaktiviert.")

    return redirect('management')

def user_list(request):
    
    User = get_user_model()
    users_all = User.objects.all()
    # 30-Tage-Fenster
    thirty_days_ago = timezone.now() - timedelta(days=30)
    # Leaderboard mit echten User-Objekten
    leaderboard_qs = (
        Basket.objects
        .filter(state=Basket.BasketState.PURCHASED, datetime__gte=thirty_days_ago)
        .select_related('user')
        .values('user')  # Gruppierung über User
        .annotate(total_spent=Sum('sum'))
        .order_by('-total_spent')[:10]
    )


    # IDs auslesen und User-Objekte laden
    user_ids = [entry['user'] for entry in leaderboard_qs]
    user_map = {u.user_id: u for u in User.objects.filter(user_id__in=user_ids)}

    # Leaderboard-Daten mit echten Usern
    leaderboard = [{
        'user': user_map[entry['user']],
        'total': entry['total_spent']
    } for entry in leaderboard_qs]

     # Specials-Kategorie finden
    specials_category = Category.objects.filter(title__iexact="Specials").first()
    specials = []

    if specials_category:
        specials = (
            BoughtArticle.objects
            .filter(
                article__category=specials_category,
                basket__state='Purchased'
            )
            .select_related('article', 'basket')
            .order_by('-basket__datetime')[:10]
        )

    return render(request, 'login.html', {
        'users': users_all,
        'leaderboard': leaderboard,
        'specials': specials,
    })



def login_pin(request, user_id):
    user = get_object_or_404(User, user_id=user_id)

    if request.method == 'POST':
        pin_entered = request.POST.get('pin')
        print(pin_entered)
        if not pin_entered:
            pin_entered = ""
        if user.pin == pin_entered:
            login(request, user)
            return redirect('home')  # oder wohin du willst nach Login
        else:
            messages.error(request, 'Falscher PIN')

    return render(request, 'login_pin.html', {'user': user})

@login_required(login_url='/login/')
def home(request):
    user = request.user
    categories = Category.objects.prefetch_related('article_set').all()

    # Aktiven Warenkorb holen oder erstellen
    basket, _ = Basket.objects.get_or_create(
        user=user,
        state=Basket.BasketState.OPEN,
        defaults={'datetime': timezone.now()}
    )

    bought_articles = basket.bought_articles.select_related('article').all()
    total = sum(ba.article.price * ba.amount for ba in bought_articles)

    # Wallet des Users
    wallet = Wallet.objects.get(user=user)

    recommended_article = None
    original_article = None

    recommended_id = request.session.pop('recommended_article_id', None)
    original_id = request.session.pop('original_article_id', None)

    if recommended_id:
        try:
            recommended_article = Article.objects.get(article_id=recommended_id)
        except Article.DoesNotExist:
            pass

    if original_id:
        try:
            original_article = Article.objects.get(article_id=original_id)
        except Article.DoesNotExist:
            pass


    return render(request, 'home.html', {
        'user': user,
        'categories': categories,
        'basket': basket,
        'bought_articles': bought_articles,
        'total': total,
        'wallet': wallet,
        'recommended_article': recommended_article,
        'original_article': original_article,
    })

@login_required(login_url='/login/')
def add_to_basket(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    basket, _ = Basket.objects.get_or_create(
        user=request.user,
        state=Basket.BasketState.OPEN,
        defaults={'datetime': timezone.now()}
    )

    bought_article, created = BoughtArticle.objects.get_or_create(
        basket=basket,
        article=article,
        defaults={'amount': 1}
    )

    if not created:
        bought_article.amount += 1
        bought_article.save()

    # Co-Purchase Analyse:
    co_article = None
    # Baskets anderer Nutzer, in denen dieser Artikel gekauft wurde
    co_baskets = Basket.objects.filter(
        bought_articles__article=article,
        state=Basket.BasketState.PURCHASED
    ).exclude(user=request.user).distinct()

    # Alle Artikel, die in diesen Co-Baskets vorkommen (außer dem Ursprungsartikel)
    co_bought_articles = BoughtArticle.objects.filter(
        basket__in=co_baskets
    ).exclude(article=article).select_related('article')

    # Ein zufälliger Co-Artikel (wenn vorhanden)
    if co_bought_articles.exists():
        co_article = random.choice(co_bought_articles).article

    # Empfehlung speichern in der Session
    request.session['recommended_article_id'] = co_article.article_id if co_article else None
    request.session['original_article_id'] = article.article_id

    return redirect('home')



@login_required(login_url='/login/')
def remove_from_basket(request, bought_article_id):
    try:
        item = BoughtArticle.objects.get(id=bought_article_id, basket__user=request.user, basket__state='Open')
        item.delete()
    except BoughtArticle.DoesNotExist:
        pass
    return redirect('home')

@login_required(login_url='/login/')
def purchase_basket(request):
    try:
        basket = Basket.objects.get(user=request.user, state=Basket.BasketState.OPEN)
        bought_articles = basket.bought_articles.select_related('article')
        
        # Gesamtsumme berechnen
        total = sum(item.article.price * item.amount for item in bought_articles)
        total = Decimal(total).quantize(Decimal('0.01'))

        # Wallet des Users laden
        wallet = Wallet.objects.get(user=request.user)

        if 0:#wallet.sum < total, lassen wir erstmal raus
            # Zu wenig Guthaben → zurück zur Seite mit Fehlermeldung
            messages.error(request, "Nicht genügend Guthaben.")
            return redirect('home')

        # Betrag abziehen
        wallet.sum -= total
        wallet.save()

        # Basket aktualisieren
        basket.sum = total
        basket.datetime = timezone.now()
        basket.state = Basket.BasketState.PURCHASED
        basket.save()

        # WalletActivity für Kauf speichern
        WalletActivity.objects.create(
            wallet=wallet,
            basket=str(basket.id),
            datetime=timezone.now(),
            description="Kauf von Warenkorb",
            activity_type=WalletActivity.ActivityType.DEBIT,
            beleg_id=f"BASKET-{basket.id}",
            amount=total
        )

        # Optional: MesseWallet gegenbuchen? → siehe vorherige Logik

    except Basket.DoesNotExist:
        messages.error(request, "Kein aktiver Warenkorb gefunden.")
    except Wallet.DoesNotExist:
        messages.error(request, "Wallet nicht gefunden.")

    return redirect('home')

from django.views.decorators.csrf import csrf_exempt

@login_required(login_url='/login/')
@csrf_exempt
def add_special_to_basket(request, article_id):
    if request.method == 'POST':
        description = request.POST.get('description', '').strip()
        article = get_object_or_404(Article, pk=article_id)
        basket, _ = Basket.objects.get_or_create(
            user=request.user,
            state=Basket.BasketState.OPEN,
            defaults={'datetime': timezone.now()}
        )

        BoughtArticle.objects.create(
            basket=basket,
            article=article,
            amount=1,
            description=description
        )

    return redirect('home')

@require_POST
@login_required
def update_basket_quantity(request, bought_article_id):
    new_amount = int(request.POST.get('amount', 1))

    bought_article = get_object_or_404(BoughtArticle, id=bought_article_id, basket__user=request.user, basket__state=Basket.BasketState.OPEN)

    if new_amount >= 1 and new_amount <= 10:
        bought_article.amount = new_amount
        bought_article.save()
        messages.success(request, f"Anzahl für {bought_article.article.title} aktualisiert.")
    else:
        messages.error(request, "Ungültige Menge.")

    return redirect('home')


@login_required(login_url='/login/')
def management(request):
    if not request.user.is_superuser:
        messages.error(request, "Zugriff verweigert.")
        return redirect('home')

    wallet = Wallet.objects.get(user=request.user)

    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            amount = Decimal(request.POST.get('amount'))
            description = request.POST.get('description').strip()
            beleg_id = request.POST.get('beleg_id', '').strip()

            if amount <= 0:
                messages.error(request, "Betrag muss positiv sein.")
                return redirect('management')

            # Betrag anpassen
            if action == 'Deposit':
                wallet.sum += amount
            elif action == 'Debit':
                if wallet.sum < amount:
                    messages.error(request, "Nicht genügend Guthaben für Auszahlung.")
                    return redirect('management')
                wallet.sum -= amount
            else:
                messages.error(request, "Ungültige Aktion.")
                return redirect('management')

            wallet.save()

            # Log: WalletActivity
            WalletActivity.objects.create(
            wallet=wallet,
            basket="Admin-Aktion",
            datetime=timezone.now(),
            description=description,
            activity_type=action,
            beleg_id=beleg_id,
            amount=amount
        )

            messages.success(request, f"{action} erfolgreich gebucht: {amount} €")

        except (InvalidOperation, ValueError):
            messages.error(request, "Ungültiger Betrag.")
        except Exception as e:
            messages.error(request, f"Fehler: {str(e)}")
    users = User.objects.all()

    # Wallets als Dictionary für schnellen Zugriff
    wallets = {w.user_id: w.sum for w in Wallet.objects.all()}
    super_wallet = Wallet.objects.get(user=request.user)

    super_activities = (
        WalletActivity.objects
        .filter(wallet=super_wallet, activity_type__in=["Deposit", "Debit"])
        .order_by('-datetime')[:20]
    )
    return render(request, 'management.html', {
        'wallet': wallet,
        'users': users,
        'wallets': wallets,
        'super_activities': super_activities,
    })

@login_required
@require_POST
def messebeitraege_buchen(request):
    if not request.user.is_superuser:
        messages.error(request, "Zugriff verweigert.")
        return redirect('management')

    User = get_user_model()
    users = User.objects.filter(is_active=True).exclude(user_id=request.user.user_id)
    now = timezone.now()
    beschreibung = f"Messebeitrag {now.strftime('%m/%Y')}"
    beitrag = Decimal('20.00')
    count = 0

    for user in users:
        wallet = Wallet.objects.filter(user=user).first()
        if wallet:
            wallet.sum -= beitrag
            wallet.save()

            WalletActivity.objects.create(
                wallet=wallet,
                basket="Messebeitrag",
                datetime=now,
                description=beschreibung,
                activity_type="Debit",
                beleg_id=f"MESSEBEITRAG-{now.strftime('%m%y')}-{user.user_id}",
                amount=beitrag
            )
            count += 1

    messages.success(request, f"Messebeitrag von {beitrag} € für {count} Nutzer erfolgreich gebucht.")
    return redirect('management')

@login_required(login_url='/login/')
def marinerechnung(request):
    if not request.user.is_superuser:
        messages.error(request, "Zugriff verweigert.")
        return redirect('home')

    User = get_user_model()
    users = User.objects.filter(is_active=True)

    if request.method == 'POST':
        selected_user_ids = request.POST.getlist('users')
        amount_total = Decimal(request.POST.get('amount'))
        description = request.POST.get('description', '').strip() or "Gemeinsame Rechnung"

        if not selected_user_ids:
            messages.error(request, "Keine Nutzer ausgewählt.")
            return redirect('marinerechnung')

        if amount_total <= 0:
            messages.error(request, "Betrag muss positiv sein.")
            return redirect('marinerechnung')

        selected_users = User.objects.filter(user_id__in=selected_user_ids)
        num_users = selected_users.count()
        amount_per_user = (amount_total / num_users).quantize(Decimal("0.01"))

        for user in selected_users:
            try:
                wallet = Wallet.objects.get(user=user)
                if wallet.sum < amount_per_user:
                    messages.warning(request, f"{user.name} hat nicht genug Guthaben!")

                # Betrag abziehen
                wallet.sum -= amount_per_user
                wallet.save()

                WalletActivity.objects.create(
                    wallet=wallet,
                    basket="Marinerechnung",
                    datetime=timezone.now(),
                    description=description,
                    activity_type=WalletActivity.ActivityType.DEBIT,
                    beleg_id=f"MARINE-{timezone.now().strftime('%Y%m%d%H%M%S')}-{user.user_id}",
                    amount=amount_per_user
                )

            except Wallet.DoesNotExist:
                messages.error(request, f"Wallet für {user.user_id} nicht gefunden.")

        messages.success(request, f"Marinerechnung über {amount_total} € auf {num_users} Personen verteilt.")
        return redirect('marinerechnung')

    return render(request, 'marinerechnung.html', {'users': users})

@login_required(login_url='/login/')
def einzahlung(request):
    if not request.user.is_superuser:
        messages.error(request, "Zugriff verweigert.")
        return redirect('home')

    User = get_user_model()
    users = User.objects.filter(is_active=True).exclude(user_id=request.user.user_id)  # alle außer Superuser
    super_wallet = Wallet.objects.get(user=request.user)

    if request.method == 'POST':
        for user in users:
            input_name = f"betrag_{user.user_id}"
            raw_value = request.POST.get(input_name)

            try:
                amount = Decimal(raw_value)
            except:
                continue  # Kein gültiger Wert → überspringen

            if amount == 0:
                continue  # Nichts zu tun

            # Nutzer-Wallet
            try:
                user_wallet = Wallet.objects.get(user=user)
            except Wallet.DoesNotExist:
                messages.error(request, f"Wallet für {user.user_id} nicht gefunden.")
                continue

            # 1. Buchung für den Nutzer
            user_wallet.sum += amount
            user_wallet.save()

            WalletActivity.objects.create(
                wallet=user_wallet,
                basket="Admin-Einzahlung",
                datetime=timezone.now(),
                description="Admingesteuerte Änderung durch Superuser",
                activity_type="Deposit" if amount > 0 else "Debit",
                beleg_id=f"ADMIN-{timezone.now().strftime('%Y%m%d%H%M%S')}-{user.user_id}",
                amount=abs(amount)
            )

            # 2. Gegenbuchung für Superuser
            super_wallet.sum += amount
            super_wallet.save()

            WalletActivity.objects.create(
                wallet=super_wallet,
                basket="Admin-Gegenbuchung",
                datetime=timezone.now(),
                description=f"Gegenbuchung für {user.name}",
                activity_type="Deposit" if amount > 0 else "Debit",
                beleg_id=f"GEGEN-{timezone.now().strftime('%Y%m%d%H%M%S')}-{user.user_id}",
                amount=abs(amount)
            )

        messages.success(request, "Einzahlungen/Auszahlungen erfolgreich verarbeitet.")
        return redirect('einzahlung')
    # Letzte 20 Wallet-Transaktionen (nur Ein-/Auszahlungen)
    transaktionen = (
        WalletActivity.objects
        .filter(activity_type__in=["Deposit", "Debit"])
        .select_related('wallet__user')
        .order_by('-datetime')[:20]
    )
    # Daten für das Template
    wallets = {w.user_id: w.sum for w in Wallet.objects.filter(user__in=users)}
    return render(request, 'einzahlung.html', {
        'users': users,
        'wallets': wallets,
        'transaktionen': transaktionen,
    })


@login_required(login_url='/login/')
def ueberblick(request):
    # Die 10 letzten gekauften Warenkörbe
    baskets = (
        Basket.objects
        .filter(user=request.user, state=Basket.BasketState.PURCHASED)
        .order_by('-datetime')[:10]
        .prefetch_related('bought_articles__article')
    )
     # Kategorie-Auswertung
    category_counts = defaultdict(int)
    for basket in baskets:
        for item in basket.bought_articles.all():
            category = item.article.category
            category_counts[category.title] += item.amount

    # Für Chart.js vorbereiten
    radar_labels = list(category_counts.keys())
    radar_data = list(category_counts.values())

    wallet = Wallet.objects.get(user=request.user)


    return render(request, 'ueberblick.html', {
        'baskets': baskets,
        'radar_labels': radar_labels,
        'radar_data': radar_data,
        'wallet':wallet
    })

@login_required
def monatsuebersicht(request):
    if not request.user.is_superuser:
        messages.error(request, "Zugriff verweigert.")
        return redirect('home')

    User = get_user_model()
    selected_month = request.GET.get('month')
    daten = []
    # Alle Monate mit Käufen
    aktive_monate_qs = (
        Basket.objects
        .filter(state=Basket.BasketState.PURCHASED)
        .annotate(month=TruncMonth('datetime'))
        .values_list('month', flat=True)
        .distinct()
        .order_by('-month')
    )

    # Umwandeln in string-Format "YYYY-MM"
    aktive_monate = [dt.strftime("%Y-%m") for dt in aktive_monate_qs]
    if selected_month:
        try:
            year, month = map(int, selected_month.split('-'))
            start = datetime(year, month, 1)
            end = datetime(year + int(month == 12), (month % 12) + 1, 1)
        except ValueError:
            messages.error(request, "Ungültiges Monatsformat.")
            return redirect('monatsuebersicht')

        specials_cat = Category.objects.filter(title__iexact="Specials").first()
        all_users = User.objects.all()

        for user in all_users:
            baskets = Basket.objects.filter(
                user=user,
                state=Basket.BasketState.PURCHASED,
                datetime__gte=start,
                datetime__lt=end
            ).prefetch_related('bought_articles__article')

            if not baskets.exists():
                continue

            kauf_summe = sum(b.sum for b in baskets)
            wallet = Wallet.objects.filter(user=user).first()

            marine_activities = WalletActivity.objects.filter(
                wallet__user=user,
                basket__icontains="Marinerechnung",
                datetime__gte=start,
                datetime__lt=end
            )

            specials_count = 0
            if specials_cat:
                for basket in baskets:
                    for item in basket.bought_articles.all():
                        if item.article.category_id == specials_cat.category_id:
                            specials_count += item.amount

            daten.append({
                'user': user,
                'wallet_sum': wallet.sum if wallet else 0,
                'kauf_summe': kauf_summe,
                'specials_count': specials_count,
                'marinerechnungen': marine_activities
            })

    # 🟢 Dieser Teil ist jetzt **immer** aktiv, auch ohne Monat
    negativ_nutzer = []
    negativ_summe = Decimal("0.00")

    for user in User.objects.all():
        wallet = Wallet.objects.filter(user=user).first()
        if wallet and wallet.sum < 0:
            negativ_nutzer.append({'user': user, 'saldo': wallet.sum})
            negativ_summe += wallet.sum

    return render(request, 'monatsuebersicht.html', {
        'daten': daten,
        'selected_month': selected_month,
        'aktive_monate': aktive_monate,
        'negativ_nutzer': negativ_nutzer,
        'negativ_summe': negativ_summe,
    })

@login_required
def sende_saldoerinnerung(request):
    if not request.user.is_superuser:
        messages.error(request, "Zugriff verweigert.")
        return redirect('home')

    User = get_user_model()
    users = User.objects.filter(is_active=True)
    negative_users = []

    for user in users:
        wallet = Wallet.objects.filter(user=user).first()
        if wallet and wallet.sum < 0:
            # PayPal-Link vorbereiten (z. B. mit Betrag) #
            paypal_link = Settings.objects.first().paypal_link #f"https://www.paypal.com/paypalme/messeverein/{abs(wallet.sum):.2f}" #change

            # Mail-Inhalt aus Template generieren
            message = render_to_string('email/saldo_erinnerung.txt', {
                'user': user,
                'betrag': abs(wallet.sum),
                'paypal_link': paypal_link,
            })

            send_mail(
                subject='🧾 Deine O-Messe Rechnung ist fällig',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email_address],
                fail_silently=False
            )

            negative_users.append(user.user_id)

    messages.success(request, f"E-Mails an {len(negative_users)} Nutzer mit negativem Saldo gesendet.")
    return redirect('monatsuebersicht')