from django.db import migrations


def seed(apps, schema_editor):
    Kafedra = apps.get_model('app', 'Kafedra')
    Oqituvchi = apps.get_model('app', 'Oqituvchi')
    FanYuklama = apps.get_model('app', 'FanYuklama')

    kafedra, _ = Kafedra.objects.get_or_create(nomi="Geoaxborot texnologiyalari")

    oqituvchi, _ = Oqituvchi.objects.get_or_create(
        ism="F.",
        familiya="Shokirov",
        defaults={
            'lavozim': 'dotsent',
            'kafedra': kafedra,
            'stavka': 1.0,
            'stavka_turi': 'asosiy',
        },
    )

    rows = [
        # 1-semestr
        dict(semestr=1, fan_nomi="Geoaxborot texnologiyalari (Y)", yonalish="KI", fakultet="KI",
             kredit=6, kurs=4, talabalar_soni=63, potok_soni=1, guruh_soni=3, kichik_guruh=3,
             maruza_jami=30, amaliyot_jami=44, laboratoriya_jami=36,
             reyting_1ob_turi='y', reyting_1ob_soati=1, reyting_ob_turi='y', reyting_ob_soati=3,
             reyting_yb_turi='y', reyting_yb_soati=19),
        dict(semestr=1, fan_nomi="Geoaxborot texnologiyalari-sirtqi (Y)", yonalish="KI", fakultet="KI",
             kredit=6, kurs=4, talabalar_soni=129, potok_soni=2, guruh_soni=5, kichik_guruh=3,
             maruza_jami=30, amaliyot_jami=44, laboratoriya_jami=60,
             reyting_1ob_turi='y', reyting_1ob_soati=1, reyting_ob_turi='y', reyting_ob_soati=13,
             reyting_yb_turi='y', reyting_yb_soati=39),
        dict(semestr=1, fan_nomi="Masofadan zondlash (Y) - masofaviy", yonalish="KI", fakultet="KI",
             kredit=6, kurs=4, talabalar_soni=0, potok_soni=0, guruh_soni=0, kichik_guruh=0,
             reyting_yb_turi='y', reyting_yb_soati=39),
        dict(semestr=1, fan_nomi="BMI (rahbarlik)", yonalish="KI", fakultet="KI",
             kredit=0, kurs=4, bmi=84,
             izoh="Bitiruv malakaviy ishi"),
        # 2-semestr
        dict(semestr=2, fan_nomi="Mobil ilovalarni ishlab chiqish (Y)", yonalish="DI", fakultet="KI",
             kredit=6, kurs=3, talabalar_soni=64, potok_soni=1, guruh_soni=2, kichik_guruh=2,
             maruza_jami=42, amaliyot_jami=30,
             reyting_1ob_turi='y', reyting_1ob_soati=1, reyting_ob_turi='y', reyting_ob_soati=13,
             reyting_yb_turi='y', reyting_yb_soati=19),
        dict(semestr=2, fan_nomi="Masofaviy amaliyot", yonalish="AKT", fakultet="TTKT",
             kurs=3, amaliyot_soati=180, izoh="6 hafta x 30 soat = 180 soat"),
        dict(semestr=2, fan_nomi="BMI (rahbarlik)", yonalish="KI", fakultet="KI",
             kurs=4, bmi=84, izoh="Bitiruv malakaviy ishi"),
    ]

    for r in rows:
        obj = FanYuklama(oqituvchi=oqituvchi, oquv_yili="2024-2025", **r)
        # recompute jami
        obj.jami = (obj.maruza_jami + obj.amaliyot_jami + obj.laboratoriya_jami + obj.seminar_jami
                    + obj.reyting_1ob_soati + obj.reyting_ob_soati + obj.reyting_yb_soati
                    + obj.kurs_ishi + obj.kurs_loyihasi + obj.magistr_dissertatsiya
                    + obj.bmi + obj.rahbarlik + obj.amaliyot_soati + obj.dak + obj.ilmiy_nazariy)
        obj.save()


def unseed(apps, schema_editor):
    FanYuklama = apps.get_model('app', 'FanYuklama')
    Oqituvchi = apps.get_model('app', 'Oqituvchi')
    FanYuklama.objects.filter(oqituvchi__familiya="Shokirov").delete()
    Oqituvchi.objects.filter(familiya="Shokirov", ism="F.").delete()


class Migration(migrations.Migration):
    dependencies = [('app', '0002_oqituvchi_stavka_oqituvchi_stavka_turi_fanyuklama')]
    operations = [migrations.RunPython(seed, unseed)]
