from django.core.management.base import BaseCommand
from app.models import Kafedra, Oqituvchi, Yuklama


OQITUVCHILAR = [
    # (familiya, ism, sharif, lavozim, ilmiy_daraja, stavka, stavka_turi,
    #  maruza_soat, amaliyot_soat, lab_soat, jami_bajarilgan_foiz)
    ("Раҳимов", "А.", "Х.", "professor",     "д.т.н.",  1.0, "asosiy",   230, 110, 60,  85),
    ("Саидмуродов", "Ф.", "Б.", "dotsent",   "PhD",     1.0, "asosiy",   180, 90,  40,  78),
    ("Рашидов", "Ж.", "Р.", "dotsent",       "PhD",     1.0, "asosiy",   160, 80,  30,  80),
    ("Исмоилов", "Б.", "И.", "katta_oqituvchi", "",     1.0, "asosiy",   140, 70,  20,  72),
    ("Раҳимова", "Б.", "С.", "katta_oqituvchi", "",     1.0, "asosiy",   130, 60,  20,  70),
    ("Тоҳирова", "М.", "Б.", "oqituvchi",    "",        1.0, "asosiy",   120, 60,  0,   68),
    ("Тошматов", "А.", "Т.", "oqituvchi",    "",        1.0, "asosiy",   110, 50,  0,   65),
    ("Исмоилова", "З.", "А.", "oqituvchi",   "",        1.0, "asosiy",   100, 50,  0,   60),
    ("Нурматов", "Б.", "Н.", "oqituvchi",    "",        0.5, "orindosh", 80,  40,  0,   55),
    ("Мирзаев", "Ш.", "М.", "oqituvchi",    "",         0.5, "orindosh", 70,  30,  0,   50),
    ("Холматов", "А.", "Х.", "assistant",    "",        1.0, "asosiy",   60,  30,  0,   45),
    ("Юсупов", "Д.", "Ю.", "assistant",      "",        1.0, "asosiy",   60,  30,  0,   45),
    ("Қодиров", "Ф.", "Қ.", "stajyor",       "",        1.0, "asosiy",   40,  20,  0,   30),
    ("Маматов", "О.", "М.", "stajyor",       "",        1.0, "asosiy",   40,  20,  0,   30),
    ("Хасанов", "Ж.", "Х.", "oqituvchi",    "",         0.5, "orindosh", 50,  20,  0,   40),
    ("Бекова", "Н.", "Б.", "oqituvchi",      "",        0.5, "orindosh", 50,  20,  0,   40),
    ("Турсунов", "С.", "Т.", "katta_oqituvchi", "",     1.0, "asosiy",   120, 60,  20,  65),
    ("Каримов", "Б.", "К.", "dotsent",       "PhD",     0.5, "orindosh", 90,  40,  0,   60),
    ("Азимов", "Р.", "А.", "oqituvchi",      "",        1.0, "asosiy",   80,  40,  0,   50),
    ("Уринов", "Х.", "У.", "oqituvchi",      "",        1.0, "asosiy",   80,  40,  0,   50),
]


class Command(BaseCommand):
    help = "Rasmdagi o'qituvchilar va yuklama ma'lumotlarini bazaga kiritadi"

    def handle(self, *args, **options):
        kafedra, _ = Kafedra.objects.get_or_create(nomi="Kafedra")
        self.stdout.write(f"Kafedra: {kafedra.nomi}")

        for row in OQITUVCHILAR:
            familiya, ism, sharif, lavozim, ilmiy_daraja, stavka, stavka_turi, \
                maruza, amaliyot, lab, foiz = row

            toliq_ism = f"{ism} {sharif}".strip()

            oqituvchi, yaratildi = Oqituvchi.objects.get_or_create(
                familiya=familiya,
                ism=toliq_ism,
                defaults={
                    "lavozim": lavozim,
                    "ilmiy_daraja": ilmiy_daraja,
                    "stavka": stavka,
                    "stavka_turi": stavka_turi,
                    "kafedra": kafedra,
                },
            )

            if not yaratildi:
                self.stdout.write(f"  Mavjud: {familiya} {toliq_ism}")
            else:
                self.stdout.write(f"  Yaratildi: {familiya} {toliq_ism}")

            Yuklama.objects.get_or_create(
                oqituvchi=oqituvchi,
                oquv_yili="2024-2025",
                defaults={
                    "maruza_soat": maruza,
                    "amaliyot_soat": amaliyot,
                    "laboratoriya_soat": lab,
                    "bajarilgan_foiz": foiz,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f"\nJami {len(OQITUVCHILAR)} ta o'qituvchi va yuklama kiritildi."
        ))
