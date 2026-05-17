from datetime import time
from django.core.management.base import BaseCommand
from app.models import Kafedra, Oqituvchi, Fan, Guruh, Dars


# Рахмонов Х.А. учун тахминий дарс жадвали
# Жами: маъруза 170 соат, амалиёт 136 соат, лаборатория 68 соат
# Ҳафталик: маъруза ~5 соат, амалиёт ~4 соат, лаб ~2 соат (34 ҳафта)

FANLAR = [
    "Matematik mantiq va algoritm nazariyasi",
    "Dasturlash texnologiyalari",
    "Ma'lumotlar bazasi",
]

GURUHLAR = [
    ("AT-21",  "Axborot texnologiyalari", 2, 25),
    ("AT-22",  "Axborot texnologiyalari", 2, 24),
    ("DAS-21", "Dasturiy injiniring",     2, 22),
]

# (hafta_kuni, boshlanish, tugash, fan_nomi, guruh_nomi, turi, xona, semestr)
DARS_JADVALI = [
    # DUSHANBA
    (0, time(8, 0),  time(9, 30),  "Matematik mantiq va algoritm nazariyasi", "AT-21",  "maruza",      "308-xona", 2),
    (0, time(9, 45), time(11, 15), "Matematik mantiq va algoritm nazariyasi", "AT-22",  "maruza",      "308-xona", 2),
    (0, time(11, 30),time(13, 0),  "Dasturlash texnologiyalari",              "DAS-21", "amaliyot",    "Lab-1",    2),

    # SESHANBA
    (1, time(8, 0),  time(9, 30),  "Dasturlash texnologiyalari",              "AT-21",  "maruza",      "308-xona", 2),
    (1, time(9, 45), time(11, 15), "Dasturlash texnologiyalari",              "AT-22",  "amaliyot",    "Lab-1",    2),
    (1, time(11, 30),time(13, 0),  "Ma'lumotlar bazasi",                      "DAS-21", "laboratoriya","Lab-2",    2),

    # CHORSHANBA
    (2, time(8, 0),  time(9, 30),  "Ma'lumotlar bazasi",                      "AT-21",  "maruza",      "308-xona", 2),
    (2, time(9, 45), time(11, 15), "Ma'lumotlar bazasi",                      "AT-22",  "amaliyot",    "Lab-2",    2),
    (2, time(11, 30),time(13, 0),  "Matematik mantiq va algoritm nazariyasi", "DAS-21", "amaliyot",    "Lab-1",    2),

    # PAYSHANBA
    (3, time(8, 0),  time(9, 30),  "Dasturlash texnologiyalari",              "DAS-21", "maruza",      "308-xona", 2),
    (3, time(9, 45), time(11, 15), "Ma'lumotlar bazasi",                      "AT-21",  "amaliyot",    "Lab-2",    2),
    (3, time(11, 30),time(13, 0),  "Ma'lumotlar bazasi",                      "AT-22",  "laboratoriya","Lab-2",    2),

    # JUMA
    (4, time(8, 0),  time(9, 30),  "Matematik mantiq va algoritm nazariyasi", "AT-21",  "laboratoriya","Lab-1",    2),
    (4, time(9, 45), time(11, 15), "Matematik mantiq va algoritm nazariyasi", "AT-22",  "amaliyot",    "Lab-1",    2),
    (4, time(11, 30),time(13, 0),  "Dasturlash texnologiyalari",              "DAS-21", "laboratoriya","Lab-1",    2),
]

HAFTA_KUNLARI = {0: "Dushanba", 1: "Seshanba", 2: "Chorshanba", 3: "Payshanba", 4: "Juma"}
TURI_NOMI = {"maruza": "Ma'ruza", "amaliyot": "Amaliyot", "laboratoriya": "Laboratoriya"}


class Command(BaseCommand):
    help = "Рахмонов Х.А. учун тахминий дарс жадвалини базага киритади"

    def handle(self, *args, **options):
        kafedra, _ = Kafedra.objects.get_or_create(nomi="Kafedra")

        # Рахмоновни топамиз
        try:
            raxmonov = Oqituvchi.objects.get(familiya="Раҳмонов", ism="Х.А.")
        except Oqituvchi.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                "Рахмонов Х.А. bazada topilmadi. Avval load_rasm_data ni ishlatng."
            ))
            return

        # Fanlar
        fan_obyektlar = {}
        for fan_nomi in FANLAR:
            fan, _ = Fan.objects.get_or_create(
                nomi=fan_nomi,
                kafedra=kafedra,
                defaults={"kredit": 3},
            )
            fan_obyektlar[fan_nomi] = fan
        self.stdout.write(f"  {len(FANLAR)} ta fan tayyor.")

        # Guruhlar
        guruh_obyektlar = {}
        for nomi, yonalish, kurs, soni in GURUHLAR:
            guruh, _ = Guruh.objects.get_or_create(
                nomi=nomi,
                defaults={
                    "yonalish": yonalish,
                    "kurs": kurs,
                    "talabalar_soni": soni,
                    "kafedra": kafedra,
                },
            )
            guruh_obyektlar[nomi] = guruh
        self.stdout.write(f"  {len(GURUHLAR)} ta guruh tayyor.")

        # Dars jadvali
        yaratildi_soni = 0
        mavjud_soni = 0

        for (hafta_kuni, boshlanish, tugash, fan_nomi, guruh_nomi, turi, xona, semestr) in DARS_JADVALI:
            dars, yaratildi = Dars.objects.get_or_create(
                oqituvchi=raxmonov,
                hafta_kuni=hafta_kuni,
                boshlanish_vaqti=boshlanish,
                semestr=semestr,
                defaults={
                    "fan": fan_obyektlar[fan_nomi],
                    "guruh": guruh_obyektlar[guruh_nomi],
                    "turi": turi,
                    "xona": xona,
                    "tugash_vaqti": tugash,
                    "bajarildi": False,
                },
            )
            if yaratildi:
                yaratildi_soni += 1
                self.stdout.write(
                    f"  + {HAFTA_KUNLARI[hafta_kuni]:12s} {boshlanish.strftime('%H:%M')}-{tugash.strftime('%H:%M')}  "
                    f"{TURI_NOMI[turi]:13s}  {guruh_nomi}  {fan_nomi}"
                )
            else:
                mavjud_soni += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDars jadvali yuklandi: {yaratildi_soni} ta yangi, {mavjud_soni} ta mavjud edi."
        ))
        self.stdout.write(self.style.SUCCESS(
            "\nРахмонов Х.А. haftalik dars jadvali (taxminiy):"
            "\n  Dushanba : Ma'ruza (AT-21, AT-22) + Amaliyot (DAS-21)"
            "\n  Seshanba : Ma'ruza (AT-21) + Amaliyot (AT-22) + Lab (DAS-21)"
            "\n  Chorshanba: Ma'ruza (AT-21) + Amaliyot (AT-22, DAS-21)"
            "\n  Payshanba: Ma'ruza (DAS-21) + Amaliyot (AT-21) + Lab (AT-22)"
            "\n  Juma     : Lab (AT-21) + Amaliyot (AT-22) + Lab (DAS-21)"
        ))
