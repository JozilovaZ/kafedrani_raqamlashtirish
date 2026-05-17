from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Kafedra, Oqituvchi, Yuklama


# (familiya_ism, lavozim, ilmiy_daraja, stavka, stavka_turi,
#  maruza_reja, amaliyot_reja, lab_reja,
#  maruza_bajarildi, amaliyot_bajarildi, lab_bajarildi,
#  bajarilgan_foiz)
OQITUVCHILAR = [
    ("Раҳмонов Х.А.",      "professor",        "д.т.н.",  1.0, "asosiy",   170, 136, 68,  170, 136, 68,  100),
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

# Рахмонов учун тўлиқ юклама жадвали (reja ва bajarildi алоҳида)
RAXMONOV_YUKLAMA = {
    "maruza_reja":      170,
    "amaliyot_reja":    136,
    "lab_reja":          68,
    "maruza_soat":      170,
    "amaliyot_soat":    136,
    "laboratoriya_soat": 68,
    "bajarilgan_foiz":  100,
}


class Command(BaseCommand):
    help = "rasm1.png dagi o'qituvchilar yuklama ma'lumotlarini bazaga kiritadi"

    def handle(self, *args, **options):
        kafedra, _ = Kafedra.objects.get_or_create(nomi="Kafedra")

        # Eski noto'g'ri yozilgan Раҳимов → Раҳмонов ga o'zgartiramiz
        renamed = Oqituvchi.objects.filter(familiya="Раҳимов", ism="Х.А.").update(familiya="Раҳмонов")
        if renamed:
            self.stdout.write(f"  Nom to'g'irlandi: Раҳимов → Раҳмонов")

        for row in OQITUVCHILAR:
            (toliq_ism, lavozim, ilmiy_daraja, stavka, stavka_turi,
             maruza_r, amaliyot_r, lab_r,
             maruza_b, amaliyot_b, lab_b, foiz) = row

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

            # Рахмонов учун reja ва bajarildi алоҳида сақланади
            if familiya == "Раҳмонов" and ism == "Х.А.":
                yuklama, y_yaratildi = Yuklama.objects.get_or_create(
                    oqituvchi=oqituvchi,
                    oquv_yili="2024-2025",
                    defaults={
                        "maruza_soat":       RAXMONOV_YUKLAMA["maruza_soat"],
                        "amaliyot_soat":     RAXMONOV_YUKLAMA["amaliyot_soat"],
                        "laboratoriya_soat": RAXMONOV_YUKLAMA["laboratoriya_soat"],
                        "bajarilgan_foiz":   RAXMONOV_YUKLAMA["bajarilgan_foiz"],
                    },
                )
                if not y_yaratildi:
                    yuklama.maruza_soat       = RAXMONOV_YUKLAMA["maruza_soat"]
                    yuklama.amaliyot_soat     = RAXMONOV_YUKLAMA["amaliyot_soat"]
                    yuklama.laboratoriya_soat = RAXMONOV_YUKLAMA["laboratoriya_soat"]
                    yuklama.bajarilgan_foiz   = RAXMONOV_YUKLAMA["bajarilgan_foiz"]
                    yuklama.save()

                # Рахмонов учун Django user яратамиз
                username = "raxmonov"
                password = "Raxmonov@2025"
                user, u_yaratildi = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "first_name": "Х.А.",
                        "last_name": "Раҳмонов",
                        "is_staff": True,
                    },
                )
                if u_yaratildi:
                    user.set_password(password)
                    user.save()
                    self.stdout.write(self.style.SUCCESS(
                        f"  User yaratildi: username={username}  parol={password}"
                    ))
                else:
                    self.stdout.write(f"  User mavjud: {username}")

                # Oqituvchi ga user bog'laymiz
                if oqituvchi.user is None:
                    oqituvchi.user = user
                    oqituvchi.save()
                    self.stdout.write(f"  Oqituvchi user ga bog'landi.")
            else:
                Yuklama.objects.get_or_create(
                    oqituvchi=oqituvchi,
                    oquv_yili="2024-2025",
                    defaults={
                        "maruza_soat":       maruza_b,
                        "amaliyot_soat":     amaliyot_b,
                        "laboratoriya_soat": lab_b,
                        "bajarilgan_foiz":   foiz,
                    },
                )

        self.stdout.write(self.style.SUCCESS(
            f"\nJami {len(OQITUVCHILAR)} ta o'qituvchi kiritildi."
        ))
        self.stdout.write(self.style.SUCCESS(
            "\nРахмонов Х.А. yuklama ma'lumotlari:"
            "\n  Ma'ruza  : reja=170  bajarildi=170"
            "\n  Amaliyot : reja=136  bajarildi=136"
            "\n  Lab      : reja=68   bajarildi=68"
            "\n  Foiz     : 100%"
        ))
