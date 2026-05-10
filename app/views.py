from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from collections import defaultdict
from .models import Kafedra, Oqituvchi, Fan, Guruh, Dars, FanYuklama


def login_view(request):
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return _redirect_by_role(user)
        messages.error(request, "Login yoki parol noto'g'ri.")
    return render(request, 'login.html', {'page_title': 'Kirish'})


def _redirect_by_role(user):
    if user.is_staff or user.is_superuser:
        return redirect('dashboard')
    return redirect('teacher_dashboard')


def logout_view(request):
    auth_logout(request)
    return redirect('login')


# ─── MUDIR VIEWS ───────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('teacher_dashboard')

    kafedra = Kafedra.objects.first()
    oqituvchilar_qs = Oqituvchi.objects.all().select_related('kafedra', 'user')

    # Har bir o'qituvchi uchun yuklama hisoblash
    oqituvchilar = []
    for o in oqituvchilar_qs:
        yuklamalar = list(FanYuklama.objects.filter(oqituvchi=o))
        jami_reja = sum(y.maruza_reja + y.amaliyot_reja + y.laboratoriya_reja for y in yuklamalar)
        jami_bajarilgan = sum(y.maruza_jami + y.amaliyot_jami + y.laboratoriya_jami for y in yuklamalar)
        foiz = round(jami_bajarilgan / jami_reja * 100) if jami_reja else 0
        dars_soni = Dars.objects.filter(oqituvchi=o).count()
        oqituvchilar.append({
            'obj': o,
            'ism': o.toliq_ism,
            'lavozim': o.get_lavozim_display(),
            'lavozim_rang': _lavozim_rang(o.lavozim),
            'yuklama_foiz': foiz,
            'jami_soat': round(jami_bajarilgan),
            'jami_reja': round(jami_reja),
            'dars_soni': dars_soni,
        })

    # Umumiy soat statistikasi
    jami_maruza_reja = FanYuklama.objects.aggregate(s=Sum('maruza_reja'))['s'] or 0
    jami_amaliyot_reja = FanYuklama.objects.aggregate(s=Sum('amaliyot_reja'))['s'] or 0
    jami_lab_reja = FanYuklama.objects.aggregate(s=Sum('laboratoriya_reja'))['s'] or 0
    jami_maruza = FanYuklama.objects.aggregate(s=Sum('maruza_jami'))['s'] or 0
    jami_amaliyot = FanYuklama.objects.aggregate(s=Sum('amaliyot_jami'))['s'] or 0
    jami_lab = FanYuklama.objects.aggregate(s=Sum('laboratoriya_jami'))['s'] or 0
    jami_bajarilgan_umumiy = jami_maruza + jami_amaliyot + jami_lab
    jami_reja_umumiy = jami_maruza_reja + jami_amaliyot_reja + jami_lab_reja
    umumiy_foiz = round(jami_bajarilgan_umumiy / jami_reja_umumiy * 100) if jami_reja_umumiy else 0

    # Haftalik dars statistikasi
    jami_haftalik_dars = Dars.objects.count()
    bajarilgan_dars = Dars.objects.filter(bajarildi=True).count()

    # Top 5 faol o'qituvchilar (eng yuqori foiz)
    top_oqituvchilar = sorted(oqituvchilar, key=lambda x: x['yuklama_foiz'], reverse=True)[:5]

    # Diqqat kerak (pastki foiz, lekin reja bor)
    muammo = sorted(
        [o for o in oqituvchilar if o['jami_reja'] > 0 and o['yuklama_foiz'] < 50],
        key=lambda x: x['yuklama_foiz']
    )[:4]

    # Lavozim bo'yicha taqsimot
    from collections import Counter
    lavozim_count = Counter(o['obj'].lavozim for o in oqituvchilar)
    lavozim_stat = [
        {'nom': lbl, 'soni': lavozim_count.get(val, 0), 'rang': _lavozim_rang(val)}
        for val, lbl in Oqituvchi.LAVOZIM_CHOICES
        if lavozim_count.get(val, 0) > 0
    ]

    context = {
        'page_title': 'Dashboard',
        'active_page': 'dashboard',
        'kafedra': kafedra,
        'oqituvchilar': oqituvchilar,
        'top_oqituvchilar': top_oqituvchilar,
        'muammo_oqituvchilar': muammo,
        'umumiy_foiz': umumiy_foiz,
        'maruza_soat': round(jami_maruza),
        'amaliyot_soat': round(jami_amaliyot),
        'lab_soat': round(jami_lab),
        'maruza_reja': round(jami_maruza_reja),
        'amaliyot_reja': round(jami_amaliyot_reja),
        'lab_reja': round(jami_lab_reja),
        'jami_bajarilgan': round(jami_bajarilgan_umumiy),
        'jami_reja': round(jami_reja_umumiy),
        'oqituvchi_soni': oqituvchilar_qs.count(),
        'fan_soni': Fan.objects.count(),
        'guruh_soni': Guruh.objects.count(),
        'dars_soni': jami_haftalik_dars,
        'bajarilgan_dars': bajarilgan_dars,
        'qolgan_dars': jami_haftalik_dars - bajarilgan_dars,
        'lavozim_stat': lavozim_stat,
    }
    return render(request, 'dashboard.html', context)


def _lavozim_rang(lavozim):
    return {
        'professor': 'purple',
        'dotsent': 'blue',
        'katta_oqituvchi': 'green',
        'oqituvchi': 'teal',
        'assistant': 'orange',
        'stajyor': 'red',
    }.get(lavozim, 'gray')


@login_required
def oqituvchi_create(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('teacher_dashboard')

    kafedralar = Kafedra.objects.all()
    if request.method == 'POST':
        ism = request.POST.get('ism', '').strip()
        familiya = request.POST.get('familiya', '').strip()
        lavozim = request.POST.get('lavozim', 'oqituvchi')
        kafedra_id = request.POST.get('kafedra')
        telefon = request.POST.get('telefon', '')
        email = request.POST.get('email', '')
        ilmiy_daraja = request.POST.get('ilmiy_daraja', '')
        stavka = request.POST.get('stavka', 1.0)
        stavka_turi = request.POST.get('stavka_turi', 'asosiy')
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not ism or not familiya or not kafedra_id:
            messages.error(request, "Ism, familiya va kafedra majburiy.")
        elif username and User.objects.filter(username=username).exists():
            messages.error(request, "Bu username band.")
        else:
            kafedra = get_object_or_404(Kafedra, pk=kafedra_id)
            user = None
            if username and password:
                user = User.objects.create_user(
                    username=username, password=password,
                    first_name=ism, last_name=familiya, email=email,
                )
            rasm = request.FILES.get('rasm')
            Oqituvchi.objects.create(
                ism=ism, familiya=familiya, lavozim=lavozim,
                kafedra=kafedra, telefon=telefon, email=email,
                ilmiy_daraja=ilmiy_daraja, stavka=float(stavka),
                stavka_turi=stavka_turi, user=user,
                rasm=rasm if rasm else None,
            )
            messages.success(request, f"{ism} {familiya} qo'shildi.")
            return redirect('dashboard')

    return render(request, 'oqituvchi_form.html', {
        'kafedralar': kafedralar,
        'page_title': "O'qituvchi qo'shish",
        'active_page': 'dashboard',
    })


@login_required
def oqituvchi_update(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('teacher_dashboard')

    oqituvchi = get_object_or_404(Oqituvchi, pk=pk)
    kafedralar = Kafedra.objects.all()

    if request.method == 'POST':
        oqituvchi.ism = request.POST.get('ism', oqituvchi.ism).strip()
        oqituvchi.familiya = request.POST.get('familiya', oqituvchi.familiya).strip()
        oqituvchi.lavozim = request.POST.get('lavozim', oqituvchi.lavozim)
        kafedra_id = request.POST.get('kafedra')
        if kafedra_id:
            oqituvchi.kafedra = get_object_or_404(Kafedra, pk=kafedra_id)
        oqituvchi.telefon = request.POST.get('telefon', '')
        oqituvchi.email = request.POST.get('email', '')
        oqituvchi.ilmiy_daraja = request.POST.get('ilmiy_daraja', '')
        oqituvchi.stavka = float(request.POST.get('stavka', 1.0))
        oqituvchi.stavka_turi = request.POST.get('stavka_turi', 'asosiy')
        if request.FILES.get('rasm'):
            oqituvchi.rasm = request.FILES['rasm']
        oqituvchi.save()
        messages.success(request, "O'qituvchi ma'lumotlari yangilandi.")
        return redirect('dashboard')

    return render(request, 'oqituvchi_form.html', {
        'oqituvchi': oqituvchi,
        'kafedralar': kafedralar,
        'page_title': "O'qituvchini tahrirlash",
        'active_page': 'dashboard',
    })


@login_required
def oqituvchi_delete(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('teacher_dashboard')
    oqituvchi = get_object_or_404(Oqituvchi, pk=pk)
    if request.method == 'POST':
        name = oqituvchi.toliq_ism
        if oqituvchi.user:
            oqituvchi.user.delete()
        oqituvchi.delete()
        messages.success(request, f"{name} o'chirildi.")
        return redirect('dashboard')
    return render(request, 'oqituvchi_delete.html', {
        'oqituvchi': oqituvchi,
        'page_title': "O'chirish tasdiqi",
        'active_page': 'dashboard',
    })


@login_required
def oqituvchilar_list(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('teacher_dashboard')

    qidiruv = request.GET.get('q', '').strip()
    lavozim_filter = request.GET.get('lavozim', '')

    oqituvchilar_qs = Oqituvchi.objects.all().select_related('kafedra', 'user')
    if qidiruv:
        oqituvchilar_qs = oqituvchilar_qs.filter(
            ism__icontains=qidiruv
        ) | oqituvchilar_qs.filter(familiya__icontains=qidiruv)
    if lavozim_filter:
        oqituvchilar_qs = oqituvchilar_qs.filter(lavozim=lavozim_filter)

    oqituvchilar = []
    for o in oqituvchilar_qs:
        yuklamalar = FanYuklama.objects.filter(oqituvchi=o)
        jami_reja = sum(y.maruza_reja + y.amaliyot_reja + y.laboratoriya_reja for y in yuklamalar)
        jami_bajarilgan = sum(y.maruza_jami + y.amaliyot_jami + y.laboratoriya_jami for y in yuklamalar)
        foiz = round(jami_bajarilgan / jami_reja * 100) if jami_reja else 0
        fan_soni = FanYuklama.objects.filter(oqituvchi=o).values('fan_nomi').distinct().count()
        dars_soni = Dars.objects.filter(oqituvchi=o).count()
        oqituvchilar.append({
            'obj': o,
            'yuklama_foiz': foiz,
            'jami_soat': round(jami_bajarilgan),
            'fan_soni': fan_soni,
            'dars_soni': dars_soni,
            'lavozim_rang': _lavozim_rang(o.lavozim),
        })

    from .models import Oqituvchi as OqM
    lavozimlar = OqM.LAVOZIM_CHOICES

    return render(request, 'oqituvchilar_list.html', {
        'page_title': "O'qituvchilar",
        'active_page': 'oqituvchilar',
        'oqituvchilar': oqituvchilar,
        'jami_soni': oqituvchilar_qs.count(),
        'qidiruv': qidiruv,
        'lavozim_filter': lavozim_filter,
        'lavozimlar': lavozimlar,
    })


# ─── O'QITUVCHI VIEWS ──────────────────────────────────────────────────────────

@login_required
def teacher_dashboard(request):
    is_mudir = request.user.is_staff or request.user.is_superuser

    if is_mudir:
        oqituvchi_id = request.GET.get('oqituvchi')
        oqituvchi = Oqituvchi.objects.filter(pk=oqituvchi_id).first() if oqituvchi_id else Oqituvchi.objects.first()
    else:
        oqituvchi = Oqituvchi.objects.filter(user=request.user).first()
        if not oqituvchi:
            messages.error(request, "Profilingiz topilmadi. Mudir bilan bog'laning.")
            return redirect('login')

    return _teacher_context(request, oqituvchi, is_mudir)


def _teacher_context(request, oqituvchi, is_mudir):
    KUNLAR = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba']

    yuklama_qs = FanYuklama.objects.filter(oqituvchi=oqituvchi) if oqituvchi else FanYuklama.objects.none()
    yuklama_semestrlar_dict = defaultdict(list)
    for y in yuklama_qs:
        yuklama_semestrlar_dict[y.semestr].append(y)
    yuklama_semestrlar = sorted(yuklama_semestrlar_dict.items())

    jami_maruza_reja = sum(y.maruza_reja for y in yuklama_qs)
    jami_amaliyot_reja = sum(y.amaliyot_reja for y in yuklama_qs)
    jami_maruza_jami = sum(y.maruza_jami for y in yuklama_qs)
    jami_amaliyot_jami = sum(y.amaliyot_jami for y in yuklama_qs)
    jami_kredit = sum(y.kredit for y in yuklama_qs)
    jami_yuklama = sum(y.jami for y in yuklama_qs)
    jami_reja = jami_maruza_reja + jami_amaliyot_reja
    samaradorlik = round((jami_maruza_jami + jami_amaliyot_jami) / jami_reja * 100) if jami_reja else 0

    darslar_qs = (
        Dars.objects.filter(oqituvchi=oqituvchi).select_related('fan', 'guruh').order_by('hafta_kuni', 'boshlanish_vaqti')
        if oqituvchi else Dars.objects.none()
    )
    haftalik_dict = {i: [] for i in range(6)}
    for d in darslar_qs:
        haftalik_dict[d.hafta_kuni].append(d)
    haftalik_jadval = [(KUNLAR[i], haftalik_dict[i]) for i in range(6)]

    guruhlar = list({d.guruh for d in darslar_qs if d.guruh})

    # Fan bo'yicha statistika
    fan_statistika_dict = defaultdict(lambda: {'fan': '', 'jami': 0, 'bajarildi': 0})
    for d in darslar_qs:
        key = d.fan_id
        fan_statistika_dict[key]['fan'] = d.fan.nomi
        fan_statistika_dict[key]['jami'] += 1
        if d.bajarildi:
            fan_statistika_dict[key]['bajarildi'] += 1
    fan_statistika = []
    for item in fan_statistika_dict.values():
        item['qoldi'] = item['jami'] - item['bajarildi']
        item['foiz'] = round(item['bajarildi'] / item['jami'] * 100) if item['jami'] else 0
        fan_statistika.append(item)

    jami_dars = darslar_qs.count()
    jami_bajarildi = darslar_qs.filter(bajarildi=True).count()
    jami_qoldi = jami_dars - jami_bajarildi

    context = {
        'page_title': "O'qituvchi",
        'active_page': 'teacher',
        'oqituvchi': oqituvchi,
        'yuklama_semestrlar': yuklama_semestrlar,
        'jami_yuklama': round(jami_yuklama, 1),
        'jami_kredit': jami_kredit,
        'jami_maruza_reja': round(jami_maruza_reja),
        'jami_amaliyot_reja': round(jami_amaliyot_reja),
        'jami_maruza_jami': round(jami_maruza_jami),
        'jami_amaliyot_jami': round(jami_amaliyot_jami),
        'samaradorlik': samaradorlik,
        'haftalik_jadval': haftalik_jadval,
        'hafta_dars_soni': jami_dars,
        'guruhlar': guruhlar,
        'is_mudir': is_mudir,
        'barcha_oqituvchilar': Oqituvchi.objects.all() if is_mudir else None,
        'fan_statistika': fan_statistika,
        'jami_dars': jami_dars,
        'jami_bajarildi': jami_bajarildi,
        'jami_qoldi': jami_qoldi,
    }
    return render(request, 'teacher_dashboard.html', context)


@login_required
def dars_jadvali(request):
    is_mudir = request.user.is_staff or request.user.is_superuser
    if is_mudir:
        oqituvchi_id = request.GET.get('oqituvchi')
        oqituvchi = Oqituvchi.objects.filter(pk=oqituvchi_id).first() if oqituvchi_id else Oqituvchi.objects.first()
    else:
        oqituvchi = Oqituvchi.objects.filter(user=request.user).first()
        if not oqituvchi:
            messages.error(request, "Profilingiz topilmadi.")
            return redirect('login')

    KUNLAR = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba']
    darslar_qs = (
        Dars.objects.filter(oqituvchi=oqituvchi).select_related('fan', 'guruh')
        .order_by('hafta_kuni', 'boshlanish_vaqti')
        if oqituvchi else Dars.objects.none()
    )
    haftalik_dict = {i: [] for i in range(6)}
    for d in darslar_qs:
        haftalik_dict[d.hafta_kuni].append(d)
    haftalik_jadval = [(KUNLAR[i], haftalik_dict[i]) for i in range(6)]

    jami = darslar_qs.count()
    bajarildi = darslar_qs.filter(bajarildi=True).count()

    # Fan bo'yicha statistika
    from collections import defaultdict as dd
    fan_stat = dd(lambda: {'fan': '', 'jami': 0, 'bajarildi': 0})
    for d in darslar_qs:
        fan_stat[d.fan_id]['fan'] = d.fan.nomi
        fan_stat[d.fan_id]['jami'] += 1
        if d.bajarildi:
            fan_stat[d.fan_id]['bajarildi'] += 1
    fan_statistika = []
    for item in fan_stat.values():
        item['qoldi'] = item['jami'] - item['bajarildi']
        item['foiz'] = round(item['bajarildi'] / item['jami'] * 100) if item['jami'] else 0
        fan_statistika.append(item)

    return render(request, 'dars_jadvali.html', {
        'page_title': 'Dars jadvali',
        'active_page': 'dars_jadvali',
        'oqituvchi': oqituvchi,
        'haftalik_jadval': haftalik_jadval,
        'jami_dars': jami,
        'bajarilgan_dars': bajarildi,
        'qolgan_dars': jami - bajarildi,
        'fan_statistika': fan_statistika,
        'is_mudir': is_mudir,
        'barcha_oqituvchilar': Oqituvchi.objects.all() if is_mudir else None,
    })


@require_POST
@login_required
def dars_belgilash(request, pk):
    """O'qituvchi darsni bajarildi deb belgilaydi (toggle)."""
    dars = get_object_or_404(Dars, pk=pk)
    is_mudir = request.user.is_staff or request.user.is_superuser
    oqituvchi = Oqituvchi.objects.filter(user=request.user).first()
    if not is_mudir and (not oqituvchi or dars.oqituvchi != oqituvchi):
        return JsonResponse({'error': 'Ruxsat yo\'q'}, status=403)
    dars.bajarildi = not dars.bajarildi
    dars.save()
    return JsonResponse({'bajarildi': dars.bajarildi, 'pk': dars.pk})


# ─── DARSLAR VA GURUHLAR RO'YXAT ───────────────────────────────────────────────

@login_required
def darslar_list(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('teacher_dashboard')

    oqituvchi_filter = request.GET.get('oqituvchi', '')
    tur_filter       = request.GET.get('turi', '')
    kun_filter       = request.GET.get('kun', '')

    KUNLAR = {0: 'Dushanba', 1: 'Seshanba', 2: 'Chorshanba',
              3: 'Payshanba', 4: 'Juma', 5: 'Shanba'}

    qs = Dars.objects.select_related('fan', 'oqituvchi', 'guruh').order_by('hafta_kuni', 'boshlanish_vaqti')
    if oqituvchi_filter:
        qs = qs.filter(oqituvchi_id=oqituvchi_filter)
    if tur_filter:
        qs = qs.filter(turi=tur_filter)
    if kun_filter != '':
        try:
            qs = qs.filter(hafta_kuni=int(kun_filter))
        except ValueError:
            pass

    darslar_list_data = list(qs)

    # Kun bo'yicha guruhlash (haftalik ko'rinish uchun)
    kun_dict = {i: [] for i in range(6)}
    for d in darslar_list_data:
        kun_dict[d.hafta_kuni].append(d)
    kun_jadval = [(i, KUNLAR[i], kun_dict[i]) for i in range(6)]

    # Tur bo'yicha statistika
    from collections import Counter
    tur_count = Counter(d.turi for d in darslar_list_data)
    tur_stat = [
        {'tur': val, 'nom': lbl, 'soni': tur_count.get(val, 0)}
        for val, lbl in Dars.TURI_CHOICES
    ]

    # O'tilgan / qolgan
    bajarilgan = sum(1 for d in darslar_list_data if d.bajarildi)
    jami = len(darslar_list_data)

    # Ko'rinish rejimi: jadval yoki ro'yxat
    view_mode = request.GET.get('view', 'jadval')

    return render(request, 'darslar_list.html', {
        'page_title': 'Darslar',
        'active_page': 'darslar',
        'darslar': [{'obj': d, 'kun_nomi': KUNLAR.get(d.hafta_kuni, '')} for d in darslar_list_data],
        'kun_jadval': kun_jadval,
        'jami_soni': jami,
        'bajarilgan': bajarilgan,
        'qolgan': jami - bajarilgan,
        'tur_stat': tur_stat,
        'oqituvchilar': Oqituvchi.objects.all(),
        'oqituvchi_filter': oqituvchi_filter,
        'tur_filter': tur_filter,
        'kun_filter': kun_filter,
        'tur_choices': Dars.TURI_CHOICES,
        'kun_choices': list(KUNLAR.items()),
        'view_mode': view_mode,
    })


@login_required
def dars_delete(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('teacher_dashboard')
    dars = get_object_or_404(Dars, pk=pk)
    if request.method == 'POST':
        dars.delete()
        messages.success(request, "Dars o'chirildi.")
        return redirect('darslar_list')
    return render(request, 'dars_delete.html', {'dars': dars, 'page_title': "Darsni o'chirish"})


@login_required
def guruhlar_list(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('teacher_dashboard')

    q = request.GET.get('q', '').strip()
    kurs_filter = request.GET.get('kurs', '')

    qs = Guruh.objects.select_related('kafedra').order_by('kurs', 'nomi')
    if q:
        qs = qs.filter(nomi__icontains=q) | qs.filter(yonalish__icontains=q)
    if kurs_filter:
        try:
            qs = qs.filter(kurs=int(kurs_filter))
        except ValueError:
            pass

    return render(request, 'guruhlar_list.html', {
        'page_title': 'Guruhlar',
        'active_page': 'guruhlar',
        'guruhlar': qs,
        'jami_soni': qs.count(),
        'q': q,
        'kurs_filter': kurs_filter,
        'kurs_choices': range(1, 6),
    })


@login_required
def guruh_update(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('teacher_dashboard')
    guruh = get_object_or_404(Guruh, pk=pk)
    kafedralar = Kafedra.objects.all()
    if request.method == 'POST':
        guruh.nomi = request.POST.get('nomi', guruh.nomi).strip()
        guruh.yonalish = request.POST.get('yonalish', '')
        guruh.kurs = int(request.POST.get('kurs', guruh.kurs))
        guruh.talabalar_soni = int(request.POST.get('talabalar_soni', 0))
        kafedra_id = request.POST.get('kafedra')
        guruh.kafedra = Kafedra.objects.filter(pk=kafedra_id).first() if kafedra_id else guruh.kafedra
        guruh.save()
        messages.success(request, f"{guruh.nomi} yangilandi.")
        return redirect('guruhlar_list')
    return render(request, 'guruh_form.html', {
        'guruh': guruh,
        'kafedralar': kafedralar,
        'page_title': "Guruhni tahrirlash",
        'active_page': 'guruhlar',
    })


@login_required
def guruh_delete(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('teacher_dashboard')
    guruh = get_object_or_404(Guruh, pk=pk)
    if request.method == 'POST':
        nomi = guruh.nomi
        guruh.delete()
        messages.success(request, f"{nomi} o'chirildi.")
        return redirect('guruhlar_list')
    return render(request, 'guruh_delete.html', {'guruh': guruh, 'page_title': "Guruhni o'chirish"})


# ─── JADVAL CRUD ───────────────────────────────────────────────────────────────

@login_required
def dars_create(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('teacher_dashboard')

    oqituvchilar = Oqituvchi.objects.all()
    fanlar = Fan.objects.all()
    guruhlar = Guruh.objects.all()
    KUNLAR = [(0, 'Dushanba'), (1, 'Seshanba'), (2, 'Chorshanba'),
              (3, 'Payshanba'), (4, 'Juma'), (5, 'Shanba')]

    if request.method == 'POST':
        Dars.objects.create(
            fan=get_object_or_404(Fan, pk=request.POST['fan']),
            oqituvchi=get_object_or_404(Oqituvchi, pk=request.POST['oqituvchi']),
            guruh=Guruh.objects.filter(pk=request.POST.get('guruh')).first(),
            turi=request.POST['turi'],
            xona=request.POST.get('xona', ''),
            boshlanish_vaqti=request.POST['boshlanish_vaqti'],
            tugash_vaqti=request.POST['tugash_vaqti'],
            hafta_kuni=int(request.POST['hafta_kuni']),
            semestr=int(request.POST.get('semestr', 1)),
        )
        messages.success(request, "Dars jadvalga qo'shildi.")
        return redirect('dashboard')

    return render(request, 'dars_form.html', {
        'oqituvchilar': oqituvchilar, 'fanlar': fanlar,
        'guruhlar': guruhlar, 'kunlar': KUNLAR,
        'page_title': "Dars qo'shish", 'active_page': 'dashboard',
    })


@login_required
def guruh_create(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('teacher_dashboard')
    kafedralar = Kafedra.objects.all()
    if request.method == 'POST':
        nomi = request.POST.get('nomi', '').strip()
        if not nomi:
            messages.error(request, "Guruh nomi majburiy.")
        else:
            Guruh.objects.create(
                nomi=nomi,
                yonalish=request.POST.get('yonalish', ''),
                kurs=int(request.POST.get('kurs', 1)),
                talabalar_soni=int(request.POST.get('talabalar_soni', 0)),
                kafedra=Kafedra.objects.filter(pk=request.POST.get('kafedra')).first(),
            )
            messages.success(request, f"{nomi} guruhi qo'shildi.")
            return redirect('database')
    return render(request, 'guruh_form.html', {
        'kafedralar': kafedralar,
        'page_title': "Guruh qo'shish",
        'active_page': 'database',
    })


@login_required
def yuklama_jadvali(request):
    is_mudir = request.user.is_staff or request.user.is_superuser
    if is_mudir:
        oqituvchi_id = request.GET.get('oqituvchi')
        oqituvchi = Oqituvchi.objects.filter(pk=oqituvchi_id).first() if oqituvchi_id else Oqituvchi.objects.first()
    else:
        oqituvchi = Oqituvchi.objects.filter(user=request.user).first()
        if not oqituvchi:
            messages.error(request, "Profilingiz topilmadi.")
            return redirect('login')

    yuklama_qs = FanYuklama.objects.filter(oqituvchi=oqituvchi) if oqituvchi else FanYuklama.objects.none()

    semestr_dict = defaultdict(list)
    for y in yuklama_qs:
        semestr_dict[y.semestr].append(y)
    yuklama_semestrlar = sorted(semestr_dict.items())

    jami_maruza_reja  = sum(y.maruza_reja  for y in yuklama_qs)
    jami_amaliyot_reja = sum(y.amaliyot_reja for y in yuklama_qs)
    jami_lab_reja     = sum(y.laboratoriya_reja for y in yuklama_qs)
    jami_maruza_jami  = sum(y.maruza_jami  for y in yuklama_qs)
    jami_amaliyot_jami = sum(y.amaliyot_jami for y in yuklama_qs)
    jami_lab_jami     = sum(y.laboratoriya_jami for y in yuklama_qs)
    jami_yuklama      = sum(y.jami for y in yuklama_qs)
    jami_kredit       = sum(y.kredit for y in yuklama_qs)

    jami_reja = jami_maruza_reja + jami_amaliyot_reja + jami_lab_reja
    jami_bajarilgan = jami_maruza_jami + jami_amaliyot_jami + jami_lab_jami
    foiz = round(jami_bajarilgan / jami_reja * 100) if jami_reja else 0

    return render(request, 'yuklama_jadvali.html', {
        'page_title': 'Yuklama jadvali',
        'active_page': 'yuklama_jadvali',
        'oqituvchi': oqituvchi,
        'yuklama_semestrlar': yuklama_semestrlar,
        'jami_yuklama': round(jami_yuklama, 1),
        'jami_kredit': jami_kredit,
        'jami_maruza_reja': round(jami_maruza_reja),
        'jami_amaliyot_reja': round(jami_amaliyot_reja),
        'jami_lab_reja': round(jami_lab_reja),
        'jami_maruza_jami': round(jami_maruza_jami),
        'jami_amaliyot_jami': round(jami_amaliyot_jami),
        'jami_lab_jami': round(jami_lab_jami),
        'jami_reja': round(jami_reja),
        'jami_bajarilgan': round(jami_bajarilgan),
        'foiz': foiz,
        'is_mudir': is_mudir,
        'barcha_oqituvchilar': Oqituvchi.objects.all() if is_mudir else None,
    })


# ─── BOSHQA SAHIFALAR ──────────────────────────────────────────────────────────

@login_required
def statistika(request):
    faol_oqituvchilar = []
    for o in Oqituvchi.objects.all()[:5]:
        j = sum(y.jami for y in FanYuklama.objects.filter(oqituvchi=o))
        faol_oqituvchilar.append({'ism': o.toliq_ism, 'fan': o.get_lavozim_display(), 'soat': f'{round(j)}s'})
    context = {
        'page_title': 'Statistika', 'active_page': 'reports',
        'faol_oqituvchilar': faol_oqituvchilar,
    }
    return render(request, 'statistika.html', context)


@login_required
def planning(request):
    return render(request, 'planning.html', {
        'page_title': 'Rejalashtirish', 'active_page': 'planning', 'oquv_yili': '2024-2025',
    })


@login_required
def database(request):
    fanlar = Fan.objects.select_related('kafedra').all()
    guruhlar = Guruh.objects.all()
    oqituvchilar = Oqituvchi.objects.select_related('kafedra').all()
    return render(request, 'database.html', {
        'page_title': "Ma'lumotlar bazasi", 'active_page': 'database',
        'fanlar': fanlar, 'guruhlar': guruhlar, 'oqituvchilar': oqituvchilar,
    })


@login_required
def soat_kiritish(request):
    if request.user.is_staff or request.user.is_superuser:
        oqituvchi = Oqituvchi.objects.first()
    else:
        oqituvchi = Oqituvchi.objects.filter(user=request.user).first()
    kirimlar = FanYuklama.objects.filter(oqituvchi=oqituvchi) if oqituvchi else []
    return render(request, 'soat_kiritish.html', {
        'page_title': 'Soat kiritish', 'active_page': 'enter_hours',
        'oqituvchi': oqituvchi, 'kirimlar': kirimlar,
    })


@login_required
def tahlil(request):
    oqituvchilar_data = []
    for o in Oqituvchi.objects.all():
        yuklamalar = FanYuklama.objects.filter(oqituvchi=o)
        reja = sum(y.maruza_reja + y.amaliyot_reja for y in yuklamalar)
        bajarilgan = sum(y.maruza_jami + y.amaliyot_jami for y in yuklamalar)
        foiz = round(bajarilgan / reja * 100) if reja else 0
        oqituvchilar_data.append({
            'ism': o.toliq_ism, 'fan': o.get_lavozim_display(),
            'reja': round(reja), 'bajarilgan': round(bajarilgan),
            'qoldiq': round(reja - bajarilgan), 'foiz': foiz,
        })
    jami_reja = sum(o['reja'] for o in oqituvchilar_data)
    jami_bajarilgan = sum(o['bajarilgan'] for o in oqituvchilar_data)
    umumiy_foiz = round(jami_bajarilgan / jami_reja * 100) if jami_reja else 0
    return render(request, 'tahlil.html', {
        'page_title': 'Tahlil', 'active_page': 'analysis',
        'oqituvchilar': oqituvchilar_data,
        'jami_reja': jami_reja, 'jami_bajarilgan': jami_bajarilgan,
        'jami_qoldiq': jami_reja - jami_bajarilgan, 'umumiy_foiz': umumiy_foiz,
    })


@login_required
def hisobot(request):
    oqituvchilar_data = []
    for o in Oqituvchi.objects.all():
        yuklamalar = FanYuklama.objects.filter(oqituvchi=o)
        maruza = round(sum(y.maruza_jami for y in yuklamalar))
        amaliyot = round(sum(y.amaliyot_jami for y in yuklamalar))
        lab = round(sum(y.laboratoriya_jami for y in yuklamalar))
        reja = round(sum(y.maruza_reja + y.amaliyot_reja + y.laboratoriya_reja for y in yuklamalar))
        jami = maruza + amaliyot + lab
        foiz = round(jami / reja * 100) if reja else 0
        oqituvchilar_data.append({
            'ism': o.toliq_ism, 'maruza': maruza, 'amaliyot': amaliyot,
            'lab': lab, 'jami': jami, 'reja': reja, 'foiz': foiz,
        })
    return render(request, 'hisobot.html', {
        'page_title': 'Yakuniy hisobot', 'active_page': 'final_report',
        'semestr': '1-semestr', 'oquv_yili': '2024-2025',
        'oqituvchilar': oqituvchilar_data,
        'jami_reja': sum(o['reja'] for o in oqituvchilar_data),
        'jami_bajarilgan': sum(o['jami'] for o in oqituvchilar_data),
    })
