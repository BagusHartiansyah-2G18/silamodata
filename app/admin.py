from django.contrib import admin
from .models import TransaksiPajak,TargetPajak,PotensiBaru

@admin.register(TransaksiPajak)
class TransaksiPajakAdmin(admin.ModelAdmin):
    data = ['pengguna_nama', 'objek_nama', 'tgl_bayar', 'transaksi_jmlhbayardenda', 'status_bayar']
    list_display = data
    list_display_links = data
    search_fields = ['pengguna_nama', 'subjenispajak_nama', 'objek_nama', 'tgl_bayar']
    list_filter = ['subjenispajak_nama','tahun','bulan']


@admin.register(TargetPajak)
class TargetPajakAdmin(admin.ModelAdmin):
    data = ('subjenispajak_nama', 'target_tahun', 'target_nominal')
    list_display = data
    list_display_links = data
    search_fields = ['subjenispajak_nama']
    list_filter = ['target_tahun']


@admin.register(PotensiBaru)
class PotensiBaruAdmin(admin.ModelAdmin):
    list_display = (
        'nama_potensi',
        'perangkat_daerah_pengusul',
        'kategori_sektor',
        'status_perda',
        'target_nominal_display',
        'status_verifikasi',
        'tanggal_input',
    )
    list_filter = ('status_perda', 'status_verifikasi', 'kategori_sektor')
    search_fields = ('nama_potensi', 'perangkat_daerah_pengusul', 'nomor_perda_terkait')

    def target_nominal_display(self, obj):
        return f"{obj.nilai_estimasi:,.2f}" if obj.nilai_estimasi else "-"
    target_nominal_display.short_description = "Nilai Estimasi"
