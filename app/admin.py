from django.contrib import admin
from .models import Kafedra, Oqituvchi, Fan, Guruh, Dars, Yuklama, Reyting, OylikStatistika, FanYuklama, Talaba


@admin.register(Kafedra)
class KafedraAdmin(admin.ModelAdmin):
    list_display = ['nomi', 'mudiri']


@admin.register(Oqituvchi)
class OqituvchiAdmin(admin.ModelAdmin):
    list_display = ['ism', 'familiya', 'lavozim', 'kafedra']
    list_filter = ['lavozim', 'kafedra']


@admin.register(Fan)
class FanAdmin(admin.ModelAdmin):
    list_display = ['nomi', 'kafedra', 'kredit']


@admin.register(Guruh)
class GuruhAdmin(admin.ModelAdmin):
    list_display = ['nomi', 'yonalish', 'kurs', 'talabalar_soni', 'kafedra']
    list_filter = ['kurs', 'kafedra']


@admin.register(Dars)
class DarsAdmin(admin.ModelAdmin):
    list_display = ['fan', 'oqituvchi', 'guruh', 'turi', 'hafta_kuni', 'boshlanish_vaqti']
    list_filter = ['turi', 'hafta_kuni', 'oqituvchi']


@admin.register(Yuklama)
class YuklamaAdmin(admin.ModelAdmin):
    list_display = ['oqituvchi', 'oquv_yili', 'jami_soat', 'bajarilgan_foiz']


@admin.register(Reyting)
class ReytingAdmin(admin.ModelAdmin):
    list_display = ['oqituvchi', 'ball', 'oy']


@admin.register(FanYuklama)
class FanYuklamaAdmin(admin.ModelAdmin):
    list_display = ['oqituvchi', 'fan_nomi', 'semestr', 'kurs', 'talabalar_soni', 'jami']
    list_filter = ['semestr', 'oquv_yili', 'oqituvchi']
    search_fields = ['fan_nomi', 'oqituvchi__ism', 'oqituvchi__familiya']


@admin.register(Talaba)
class TalabaAdmin(admin.ModelAdmin):
    list_display = ['familiya', 'ism', 'sharif', 'talaba_id', 'guruh', 'jinsi']
    list_filter = ['guruh', 'jinsi']
    search_fields = ['familiya', 'ism', 'talaba_id']


@admin.register(OylikStatistika)
class OylikStatistikaAdmin(admin.ModelAdmin):
    list_display = ['kafedra', 'oy', 'bajarilgan_foiz']
