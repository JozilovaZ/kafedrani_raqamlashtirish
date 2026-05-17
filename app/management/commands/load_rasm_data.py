from django.core.management.base import BaseCommand
from app.models import Kafedra, Oqituvchi, Yuklama


# Rasmdagi ma'lumotlar (2024-2025 o'quv yili)
# (familiya_ism, lavozim, ilmiy_daraja, stavka, stavka_turi,
#  maruza_reja, amaliyot_reja, lab_reja,
#  maruza_bajarildi, amaliyot_bajarildi, lab_bajarildi,
#  bajarilgan_foiz)
OQITUVCHILAR = [
    ("Раҳимов Х.А.",       "professor",        "д.т.н.",  1.0, "asosiy",   170, 136, 68,  170, 136, 68,  100),
    ("Саидмуродов",        "dotsent",          "PhD",     1.0, "asosiy",   148, 118, 40,  148, 118, 40,  100),
    ("Рашидов",            "katta_oqituvchi",  "",        1.0, "asosiy",   136, 108, 32,  136, 108, 32,  100),
    ("Исмоилов",           "katta_oqituvchi",  "",        1.0, "asosiy",   118,  96, 24,  118,  96, 24,  100),
    ("Раҳимова",           "katta_oqituvchi",  "",        1.0, "asosiy",   114,  90,  0,  114,  90,  0,  100),
    ("Тоширов",            "oqituvchi",        "",        1.0, "asosiy",   100,  80,  0,  100,  80,  0,  100),
    ("Норматов",           "oqituvchi",        "",        1.0, "asosiy",    90,  72,  0,   90,  72,  0,  100),
    ("Исмоилова",          "oqituvchi",        "",        0.5, "orindosh",  60,  48,  0,   60,  48,  0,  100),
    ("Нурмуродов",         "assistant",        "",        1.0, "asosiy",    60,  48,  0,   60,  48,  0,  100),
    ("Хасанов",            "assistant",        "",        1.0, "asosiy",    54,  40,  0,   54,  40,  0,  100),
    ("Маматов",            "stajyor",          "",        1.0, "asosiy",    40,  32,  0,   40,  32,  0,  100),
]


class Command(BaseCommand):
    help = "rasm1.png dagi o'qituvchilar yuklama ma'lumotlarini bazaga kiritadi"

    def handle(self, *args, **options):
        kafedra, _ = Kafedra.objects.get_or_create(nomi="Kafedra")

        for row in OQITUVCHILAR:
            (toliq_ism, lavozim, ilmiy_daraja, stavka, stavka_turi,
             maruza_r, amaliyot_r, lab_r,
             maruza_b, amaliyot_b, lab_b, foiz) = row

            # Ism va familiyani ajratamiz
            qismlar = toliq_ism.split()
            familiya = qismlar[0]
            ism = " ".join(qismlar[1:]) if len(qismlar) > 1 else ""

            oqituvchi, yaratildi = Oqituvchi.objects.get_or_create(
                familiya=familiya,
                ism=ism,
                defaults={
                    "lavozim": lavozim,
                    "ilmiy_daraja": ilmiy_daraja,
                    "stavka": stavka,
                    "stavka_turi": stavka_turi,
                    "kafedra": kafedra,
                },
            )

            holat = "Yaratildi" if yaratildi else "Mavjud"
            self.stdout.write(f"  {holat}: {toliq_ism}")

            Yuklama.objects.get_or_create(
                oqituvchi=oqituvchi,
                oquv_yili="2024-2025",
                defaults={
                    "maruza_soat": maruza_b,
                    "amaliyot_soat": amaliyot_b,
                    "laboratoriya_soat": lab_b,
                    "bajarilgan_foiz": foiz,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f"\nJami {len(OQITUVCHILAR)} ta o'qituvchi kiritildi."
        ))
