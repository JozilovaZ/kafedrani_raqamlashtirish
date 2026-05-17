from django.db import models
from django.contrib.auth.models import User


class Kafedra(models.Model):
    nomi = models.CharField(max_length=200)
    mudiri = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='boshqaradigan_kafedralar')

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name_plural = "Kafedralar"


class Oqituvchi(models.Model):
    LAVOZIM_CHOICES = [
        ('professor', 'Professor'),
        ('dotsent', 'Dotsent'),
        ('katta_oqituvchi', "Katta o'qituvchi"),
        ('oqituvchi', "O'qituvchi"),
        ('assistant', 'Assistant'),
        ('stajyor', 'Stajyor'),
    ]
    STAVKA_TURI_CHOICES = [
        ('asosiy', 'Asosiy'),
        ('orindosh', "O'rindosh"),
        ('soatbay', 'Soatbay'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    ism = models.CharField(max_length=100)
    familiya = models.CharField(max_length=100)
    lavozim = models.CharField(max_length=20, choices=LAVOZIM_CHOICES, default='oqituvchi')
    kafedra = models.ForeignKey(Kafedra, on_delete=models.CASCADE, related_name='oqituvchilar')
    rasm = models.ImageField(upload_to='oqituvchilar/', blank=True, null=True)
    telefon = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    ilmiy_daraja = models.CharField(max_length=100, blank=True)
    stavka = models.FloatField(default=1.0)
    stavka_turi = models.CharField(max_length=20, choices=STAVKA_TURI_CHOICES, default='asosiy')

    def __str__(self):
        return f"{self.ism} {self.familiya}"

    @property
    def toliq_ism(self):
        return f"{self.ism} {self.familiya}"

    class Meta:
        verbose_name_plural = "O'qituvchilar"


class Fan(models.Model):
    nomi = models.CharField(max_length=200)
    kafedra = models.ForeignKey(Kafedra, on_delete=models.CASCADE, related_name='fanlar')
    kredit = models.IntegerField(default=0)

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name_plural = "Fanlar"


class Guruh(models.Model):
    nomi = models.CharField(max_length=50)
    yonalish = models.CharField(max_length=100, blank=True)
    kurs = models.IntegerField(default=1)
    talabalar_soni = models.IntegerField(default=0)
    kafedra = models.ForeignKey(Kafedra, on_delete=models.CASCADE, related_name='guruhlar', null=True, blank=True)

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name_plural = "Guruhlar"


class Talaba(models.Model):
    JINSI_CHOICES = [('erkak', 'Erkak'), ('ayol', 'Ayol')]

    guruh = models.ForeignKey(Guruh, on_delete=models.CASCADE, related_name='talabalar')
    ism = models.CharField(max_length=100)
    familiya = models.CharField(max_length=100)
    sharif = models.CharField(max_length=100, blank=True)
    talaba_id = models.CharField(max_length=20, unique=True)
    jinsi = models.CharField(max_length=10, choices=JINSI_CHOICES, default='erkak')
    tugilgan_sana = models.DateField(null=True, blank=True)
    telefon = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.familiya} {self.ism}"

    @property
    def toliq_ism(self):
        return f"{self.familiya} {self.ism} {self.sharif}".strip()

    class Meta:
        verbose_name_plural = "Talabalar"
        ordering = ['familiya', 'ism']


class Dars(models.Model):
    TURI_CHOICES = [
        ('maruza', "Ma'ruza"),
        ('amaliyot', 'Amaliyot'),
        ('laboratoriya', 'Laboratoriya'),
        ('seminar', 'Seminar'),
    ]

    fan = models.ForeignKey(Fan, on_delete=models.CASCADE, related_name='darslar')
    oqituvchi = models.ForeignKey(Oqituvchi, on_delete=models.CASCADE, related_name='darslar')
    guruh = models.ForeignKey(Guruh, on_delete=models.SET_NULL, null=True, blank=True, related_name='darslar')
    turi = models.CharField(max_length=20, choices=TURI_CHOICES)
    xona = models.CharField(max_length=20, blank=True)
    boshlanish_vaqti = models.TimeField()
    tugash_vaqti = models.TimeField()
    hafta_kuni = models.IntegerField(choices=[
        (0, 'Dushanba'), (1, 'Seshanba'), (2, 'Chorshanba'),
        (3, 'Payshanba'), (4, 'Juma'), (5, 'Shanba'),
    ])
    semestr = models.IntegerField(default=1)
    bajarildi = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.fan.nomi} - {self.get_turi_display()}"

    class Meta:
        verbose_name_plural = "Darslar"


class Yuklama(models.Model):
    oqituvchi = models.ForeignKey(Oqituvchi, on_delete=models.CASCADE, related_name='yuklamalar')
    oquv_yili = models.CharField(max_length=20)
    maruza_soat = models.FloatField(default=0)
    amaliyot_soat = models.FloatField(default=0)
    laboratoriya_soat = models.FloatField(default=0)
    jami_soat = models.FloatField(default=0)
    bajarilgan_foiz = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        self.jami_soat = self.maruza_soat + self.amaliyot_soat + self.laboratoriya_soat
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.oqituvchi} - {self.oquv_yili}"

    class Meta:
        verbose_name_plural = "Yuklamalar"


class Reyting(models.Model):
    oqituvchi = models.ForeignKey(Oqituvchi, on_delete=models.CASCADE, related_name='reytinglar')
    ball = models.FloatField(default=0)
    oy = models.DateField()
    talaba_baho = models.FloatField(default=0)
    izoh = models.TextField(blank=True)

    def __str__(self):
        return f"{self.oqituvchi} - {self.ball}"

    class Meta:
        verbose_name_plural = "Reytinglar"
        ordering = ['-oy']


class FanYuklama(models.Model):
    """O'qituvchining bir fan bo'yicha to'liq yuklama jadvali (jadval.docx asosida)."""
    oqituvchi = models.ForeignKey(Oqituvchi, on_delete=models.CASCADE, related_name='fan_yuklamalari')
    oquv_yili = models.CharField(max_length=20, default='2024-2025')
    semestr = models.IntegerField(default=1)

    fan_nomi = models.CharField(max_length=200)
    yonalish = models.CharField(max_length=50, blank=True)
    fakultet = models.CharField(max_length=50, blank=True)
    kredit = models.IntegerField(default=0)
    kurs = models.IntegerField(default=1)

    talabalar_soni = models.IntegerField(default=0)
    potok_soni = models.IntegerField(default=0)
    guruh_soni = models.IntegerField(default=0)
    kichik_guruh = models.IntegerField(default=0)

    maruza_reja = models.FloatField(default=0)
    maruza_jami = models.FloatField(default=0)
    amaliyot_reja = models.FloatField(default=0)
    amaliyot_jami = models.FloatField(default=0)
    laboratoriya_reja = models.FloatField(default=0)
    laboratoriya_jami = models.FloatField(default=0)
    seminar_reja = models.FloatField(default=0)
    seminar_jami = models.FloatField(default=0)

    reyting_1ob_turi = models.CharField(max_length=10, blank=True)
    reyting_1ob_soati = models.FloatField(default=0)
    reyting_ob_turi = models.CharField(max_length=10, blank=True)
    reyting_ob_soati = models.FloatField(default=0)
    reyting_yb_turi = models.CharField(max_length=10, blank=True)
    reyting_yb_soati = models.FloatField(default=0)

    kurs_ishi = models.FloatField(default=0)
    kurs_loyihasi = models.FloatField(default=0)
    magistr_dissertatsiya = models.FloatField(default=0)
    bmi = models.FloatField(default=0)
    rahbarlik = models.FloatField(default=0)
    amaliyot_soati = models.FloatField(default=0)
    dak = models.FloatField(default=0)
    ilmiy_nazariy = models.FloatField(default=0)

    izoh = models.CharField(max_length=200, blank=True)
    jami = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        self.jami = round(
            self.maruza_jami + self.amaliyot_jami + self.laboratoriya_jami + self.seminar_jami
            + self.reyting_1ob_soati + self.reyting_ob_soati + self.reyting_yb_soati
            + self.kurs_ishi + self.kurs_loyihasi + self.magistr_dissertatsiya
            + self.bmi + self.rahbarlik + self.amaliyot_soati + self.dak + self.ilmiy_nazariy,
            2,
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.oqituvchi} - {self.fan_nomi} ({self.semestr}-sem)"

    class Meta:
        verbose_name_plural = "Fan yuklamalari"
        ordering = ['oqituvchi', 'semestr', 'fan_nomi']


class OylikStatistika(models.Model):
    kafedra = models.ForeignKey(Kafedra, on_delete=models.CASCADE, related_name='statistikalar')
    oy = models.DateField()
    umumiy_yuklama = models.FloatField(default=0)
    bajarilgan = models.FloatField(default=0)
    bajarilgan_foiz = models.FloatField(default=0)

    def __str__(self):
        return f"{self.kafedra} - {self.oy}"

    class Meta:
        verbose_name_plural = "Oylik statistikalar"
        ordering = ['-oy']
