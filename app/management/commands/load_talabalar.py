from django.core.management.base import BaseCommand
from app.models import Guruh, Talaba


# (familiya, ism, sharif, talaba_id, jinsi)
AT21_TALABALAR = [
    ("Abdullayev",   "Jasur",      "Olimovich",    "AT21-001", "erkak"),
    ("Botirov",      "Sherzod",    "Mahmudovich",  "AT21-002", "erkak"),
    ("Valiyeva",     "Nilufar",    "Rashidovna",   "AT21-003", "ayol"),
    ("Hasanov",      "Bobur",      "Hamidovich",   "AT21-004", "erkak"),
    ("Toshmatova",   "Dilnoza",    "Sobirovna",    "AT21-005", "ayol"),
    ("Ergashev",     "Ulugbek",    "Nematovich",   "AT21-006", "erkak"),
    ("Xoliqova",     "Sarvinoz",   "Baxtiyorovna", "AT21-007", "ayol"),
    ("Mirzayev",     "Doniyor",    "Aliyevich",    "AT21-008", "erkak"),
    ("Nazarova",     "Mohira",     "Vohidovna",    "AT21-009", "ayol"),
    ("Qodirov",      "Sanjar",     "Ergashevich",  "AT21-010", "erkak"),
    ("Usmonov",      "Eldor",      "Sultonovich",  "AT21-011", "erkak"),
    ("Raximova",     "Zulfiya",    "Kamoliddinovna","AT21-012","ayol"),
    ("Karimov",      "Asilbek",    "Norqulovich",  "AT21-013", "erkak"),
    ("Sobirov",      "Murod",      "Baxtiyor",     "AT21-014", "erkak"),
    ("Yunusova",     "Feruza",     "Ismoilovna",   "AT21-015", "ayol"),
    ("Hamidov",      "Akbar",      "Xurshidovich", "AT21-016", "erkak"),
    ("Tursunova",    "Barno",      "Rustamovna",   "AT21-017", "ayol"),
    ("Normatov",     "Jahongir",   "Abdullayevich","AT21-018", "erkak"),
    ("Davlatova",    "Xurmo",      "Ibragimovna",  "AT21-019", "ayol"),
    ("Xasanov",      "Firdavs",    "Toxirovich",   "AT21-020", "erkak"),
    ("Ismoilov",     "Bekzod",     "Ravshanov",    "AT21-021", "erkak"),
    ("Qosimova",     "Lobar",      "Shamsiyevna",  "AT21-022", "ayol"),
    ("Razzaqov",     "Mansur",     "Hayotovich",   "AT21-023", "erkak"),
    ("Holiqov",      "Temur",      "Jamshidovich", "AT21-024", "erkak"),
    ("Tojiboyeva",   "Maftuna",    "Lochinbekovna","AT21-025", "ayol"),
]

AT22_TALABALAR = [
    ("Alimov",       "Shamsiddin", "Xoliqovich",   "AT22-001", "erkak"),
    ("Baxtiyorova",  "Gulnora",    "Fattoyevna",   "AT22-002", "ayol"),
    ("Choriyev",     "Ibrohim",    "Solijonovich", "AT22-003", "erkak"),
    ("Dusmatova",    "Ozoda",      "Saidovna",     "AT22-004", "ayol"),
    ("Eshmatov",     "Ravshan",    "Tursunovich",  "AT22-005", "erkak"),
    ("Fayzullayev",  "Otabek",     "Sobirovich",   "AT22-006", "erkak"),
    ("G'aniyeva",    "Malika",     "Nurboyevna",   "AT22-007", "ayol"),
    ("Haydarov",     "Nuriddin",   "Iskandarovich","AT22-008", "erkak"),
    ("Iskandarov",   "Sarvarbek",  "Toxirovich",   "AT22-009", "erkak"),
    ("Jurayev",      "Mirzo",      "Xasanovich",   "AT22-010", "erkak"),
    ("Komilov",      "Asliddin",   "Ro'ziyevich",  "AT22-011", "erkak"),
    ("Latipova",     "Sitora",     "Akbarovna",    "AT22-012", "ayol"),
    ("Mahmudov",     "Shuhrat",    "Hamroyevich",  "AT22-013", "erkak"),
    ("Nazarov",      "Bunyod",     "Qodirov",      "AT22-014", "erkak"),
    ("Ortiqov",      "Kamron",     "Musayevich",   "AT22-015", "erkak"),
    ("Po'latova",    "Nargiza",    "Turgunovna",   "AT22-016", "ayol"),
    ("Qurbonov",     "Laziz",      "Mahmudovich",  "AT22-017", "erkak"),
    ("Rajabov",      "Umid",       "Norbo'tayevich","AT22-018","erkak"),
    ("Sultonova",    "Hulkar",     "Baxtiyorovna", "AT22-019", "ayol"),
    ("Tohirov",      "Amir",       "Shamsiyevich", "AT22-020", "erkak"),
    ("Umarov",       "Lochinbek",  "Nishonovich",  "AT22-021", "erkak"),
    ("Valiyev",      "Sarvar",     "Qodirov",      "AT22-022", "erkak"),
    ("Xo'jayev",     "Humoyun",    "Abdullayev",   "AT22-023", "erkak"),
    ("Yusupova",     "Dilorom",    "Raximovna",    "AT22-024", "ayol"),
]

DAS21_TALABALAR = [
    ("Abduraxmonov", "Islom",      "Shavkatovich", "DAS21-001","erkak"),
    ("Boymurodova",  "Sabrina",    "Ilhomovna",    "DAS21-002","ayol"),
    ("Davlatov",     "Furqat",     "Normurodovich","DAS21-003","erkak"),
    ("Fattoyev",     "Zafar",      "Baxromovich",  "DAS21-004","erkak"),
    ("G'ulomov",     "Ilyos",      "Xasanovich",   "DAS21-005","erkak"),
    ("Hamroyev",     "Jasurbek",   "Olimovich",    "DAS21-006","erkak"),
    ("Isoqov",       "Nodir",      "Toshmatovich", "DAS21-007","erkak"),
    ("Kalandarov",   "Asilbek",    "Fattoyevich",  "DAS21-008","erkak"),
    ("Mamadaliyev",  "Eldor",      "Sotvoldiyevich","DAS21-009","erkak"),
    ("Nishonov",     "Behruz",     "Ravshanov",    "DAS21-010","erkak"),
    ("Ortiqova",     "Shahnoza",   "Baxtiyorovna", "DAS21-011","ayol"),
    ("Pulatov",      "Tohirjon",   "Ergashevich",  "DAS21-012","erkak"),
    ("Qoraboyev",    "Muslimbek",  "Hayotovich",   "DAS21-013","erkak"),
    ("Rashidova",    "Dilrabo",    "Sobirovna",    "DAS21-014","ayol"),
    ("Saidov",       "Muhammadali","Tursunovich",  "DAS21-015","erkak"),
    ("Toshpulatov",  "Sherzod",    "Norqulovich",  "DAS21-016","erkak"),
    ("Usmonova",     "Iroda",      "Xurshidovna",  "DAS21-017","ayol"),
    ("Xolmatov",     "Boburbek",   "Aliyevich",    "DAS21-018","erkak"),
    ("Yodgorov",     "Otabek",     "Iskandarov",   "DAS21-019","erkak"),
    ("Zokirov",      "Murod",      "Ibragimovich", "DAS21-020","erkak"),
    ("Aliyeva",      "Kamola",     "Mansurovna",   "DAS21-021","ayol"),
    ("Baxtiyorov",   "Farhod",     "Nematullayev", "DAS21-022","erkak"),
]

GURUH_TALABALAR = {
    "AT-21":  AT21_TALABALAR,
    "AT-22":  AT22_TALABALAR,
    "DAS-21": DAS21_TALABALAR,
}


class Command(BaseCommand):
    help = "Guruhlarga tahminiy talabalar ma'lumotlarini kiritadi"

    def handle(self, *args, **options):
        jami_yaratildi = 0
        jami_mavjud = 0

        for guruh_nomi, talabalar in GURUH_TALABALAR.items():
            guruh = Guruh.objects.filter(nomi=guruh_nomi).first()
            if not guruh:
                self.stdout.write(self.style.WARNING(
                    f"  Guruh topilmadi: {guruh_nomi} — avval load_dars_jadval ni ishlatng"
                ))
                continue

            self.stdout.write(f"\n  {guruh_nomi} guruhi ({len(talabalar)} talaba):")
            for familiya, ism, sharif, talaba_id, jinsi in talabalar:
                talaba, yaratildi = Talaba.objects.get_or_create(
                    talaba_id=talaba_id,
                    defaults={
                        "guruh":    guruh,
                        "ism":      ism,
                        "familiya": familiya,
                        "sharif":   sharif,
                        "jinsi":    jinsi,
                    },
                )
                if yaratildi:
                    jami_yaratildi += 1
                else:
                    jami_mavjud += 1

            # Guruhning talabalar_soni ni yangilab qo'yamiz
            guruh.talabalar_soni = Talaba.objects.filter(guruh=guruh).count()
            guruh.save()
            self.stdout.write(f"    Jami: {guruh.talabalar_soni} ta talaba")

        self.stdout.write(self.style.SUCCESS(
            f"\nTayyor! Yangi: {jami_yaratildi}, mavjud: {jami_mavjud}"
        ))
