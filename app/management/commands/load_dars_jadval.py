from datetime import time
from django.core.management.base import BaseCommand
from app.models import Kafedra, Oqituvchi, Fan, Guruh, Dars, FanYuklama


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
    (0, time(8,  0), time(9,  30), "Matematik mantiq va algoritm nazariyasi", "AT-21",  "maruza",      "308-xona", 2),
    (0, time(9, 45), time(11, 15), "Matematik mantiq va algoritm nazariyasi", "AT-22",  "maruza",      "308-xona", 2),
    (0, time(11,30), time(13,  0), "Dasturlash texnologiyalari",              "DAS-21", "amaliyot",    "Lab-1",    2),
    # SESHANBA
    (1, time(8,  0), time(9,  30), "Dasturlash texnologiyalari",              "AT-21",  "maruza",      "308-xona", 2),
    (1, time(9, 45), time(11, 15), "Dasturlash texnologiyalari",              "AT-22",  "amaliyot",    "Lab-1",    2),
    (1, time(11,30), time(13,  0), "Ma'lumotlar bazasi",                      "DAS-21", "laboratoriya","Lab-2",    2),
    # CHORSHANBA
    (2, time(8,  0), time(9,  30), "Ma'lumotlar bazasi",                      "AT-21",  "maruza",      "308-xona", 2),
    (2, time(9, 45), time(11, 15), "Ma'lumotlar bazasi",                      "AT-22",  "amaliyot",    "Lab-2",    2),
    (2, time(11,30), time(13,  0), "Matematik mantiq va algoritm nazariyasi", "DAS-21", "amaliyot",    "Lab-1",    2),
    # PAYSHANBA
    (3, time(8,  0), time(9,  30), "Dasturlash texnologiyalari",              "DAS-21", "maruza",      "308-xona", 2),
    (3, time(9, 45), time(11, 15), "Ma'lumotlar bazasi",                      "AT-21",  "amaliyot",    "Lab-2",    2),
    (3, time(11,30), time(13,  0), "Ma'lumotlar bazasi",                      "AT-22",  "laboratoriya","Lab-2",    2),
    # JUMA
    (4, time(8,  0), time(9,  30), "Matematik mantiq va algoritm nazariyasi", "AT-21",  "laboratoriya","Lab-1",    2),
    (4, time(9, 45), time(11, 15), "Matematik mantiq va algoritm nazariyasi", "AT-22",  "amaliyot",    "Lab-1",    2),
    (4, time(11,30), time(13,  0), "Dasturlash texnologiyalari",              "DAS-21", "laboratoriya","Lab-1",    2),
]

# View FanYuklama dan o'qiydi — har bir fan uchun reja va bajarildi soatlar
# Jami: ma'ruza 170, amaliyot 136, lab 68 (uchta fanga taqsimlangan)
FAN_YUKLAMALAR = [
    # (fan_nomi, semestr, kredit, maruza_reja, amaliyot_reja, lab_reja,
    #  maruza_jami, amaliyot_jami, lab_jami)
    ("Matematik mantiq va algoritm nazariyasi", 2, 3,  60, 48, 24,  60, 48, 24),
    ("Dasturlash texnologiyalari",              2, 3,  60, 48, 22,  60, 48, 22),
    ("Ma'lumotlar bazasi",                      2, 3,  50, 40, 22,  50, 40, 22),
]

HAFTA_KUNLARI = {0: "Dushanba", 1: "Seshanba", 2: "Chorshanba", 3: "Payshanba", 4: "Juma"}
TURI_NOMI = {"maruza": "Ma'ruza", "amaliyot": "Amaliyot", "laboratoriya": "Laboratoriya"}


class Command(BaseCommand):
    help = "Рахмонов Х.А. учун тахминий дарс жадвали ва FanYuklama ни базага киритади"

    def handle(self, *args, **options):
        kafedra, _ = Kafedra.objects.get_or_create(nomi="Kafedra")

        try:
            raxmonov = Oqituvchi.objects.get(familiya="Раҳмонов", ism="Х.А.")
        except Oqituvchi.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                "Рахмонов Х.А. bazada topilmadi. Avval load_rasm_data ni ishlatng."
            ))
            return

        # 1. Fanlar
        fan_obyektlar = {}
        for fan_nomi in FANLAR:
            fan, _ = Fan.objects.get_or_create(
                nomi=fan_nomi, kafedra=kafedra, defaults={"kredit": 3}
            )
            fan_obyektlar[fan_nomi] = fan
        self.stdout.write(f"  {len(FANLAR)} ta fan tayyor.")

        # 2. Guruhlar
        guruh_obyektlar = {}
        for nomi, yonalish, kurs, soni in GURUHLAR:
            guruh, _ = Guruh.objects.get_or_create(
                nomi=nomi,
                defaults={"yonalish": yonalish, "kurs": kurs,
                          "talabalar_soni": soni, "kafedra": kafedra},
            )
            guruh_obyektlar[nomi] = guruh
        self.stdout.write(f"  {len(GURUHLAR)} ta guruh tayyor.")

        # 3. FanYuklama — view shu modeldan o'qiydi
        self.stdout.write("\n  FanYuklama kiritilmoqda...")
        for (fan_nomi, semestr, kredit,
             mar_r, amal_r, lab_r,
             mar_j, amal_j, lab_j) in FAN_YUKLAMALAR:

            fy, yaratildi = FanYuklama.objects.get_or_create(
                oqituvchi=raxmonov,
                fan_nomi=fan_nomi,
                oquv_yili="2024-2025",
                semestr=semestr,
                defaults={
                    "kredit":             kredit,
                    "maruza_reja":        mar_r,
                    "amaliyot_reja":      amal_r,
                    "laboratoriya_reja":  lab_r,
                    "maruza_jami":        mar_j,
                    "amaliyot_jami":      amal_j,
                    "laboratoriya_jami":  lab_j,
                },
            )
            if not yaratildi:
                fy.kredit            = kredit
                fy.maruza_reja       = mar_r
                fy.amaliyot_reja     = amal_r
                fy.laboratoriya_reja = lab_r
                fy.maruza_jami       = mar_j
                fy.amaliyot_jami     = amal_j
                fy.laboratoriya_jami = lab_j
                fy.save()
            holat = "Yaratildi" if yaratildi else "Yangilandi"
            self.stdout.write(f"    {holat}: {fan_nomi}")

        # 4. Dars jadvali
        self.stdout.write("\n  Dars jadvali kiritilmoqda...")
        yaratildi_soni = mavjud_soni = 0

        for (hafta_kuni, boshlanish, tugash,
             fan_nomi, guruh_nomi, turi, xona, semestr) in DARS_JADVALI:
            dars, yaratildi = Dars.objects.get_or_create(
                oqituvchi=raxmonov,
                hafta_kuni=hafta_kuni,
                boshlanish_vaqti=boshlanish,
                semestr=semestr,
                defaults={
                    "fan":            fan_obyektlar[fan_nomi],
                    "guruh":          guruh_obyektlar[guruh_nomi],
                    "turi":           turi,
                    "xona":           xona,
                    "tugash_vaqti":   tugash,
                    "bajarildi":      False,
                },
            )
            if yaratildi:
                yaratildi_soni += 1
                self.stdout.write(
                    f"    + {HAFTA_KUNLARI[hafta_kuni]:12s} "
                    f"{boshlanish.strftime('%H:%M')}-{tugash.strftime('%H:%M')}  "
                    f"{TURI_NOMI[turi]:13s}  {guruh_nomi}"
                )
            else:
                mavjud_soni += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nTayyor! Dars jadvali: {yaratildi_soni} yangi, {mavjud_soni} mavjud."
        ))
        self.stdout.write(self.style.SUCCESS(
            "FanYuklama jami:"
            "\n  Ma'ruza  : reja=170  bajarildi=170"
            "\n  Amaliyot : reja=136  bajarildi=136"
            "\n  Lab      : reja=68   bajarildi=68"
            "\n  Haftalik dars slotlari: 15 ta"
        ))
