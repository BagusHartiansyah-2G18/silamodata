from django.contrib import admin
from .models import TransaksiPajak

@admin.register(TransaksiPajak)
class TransaksiPajakAdmin(admin.ModelAdmin):
    data = ['pengguna_nama', 'objek_nama', 'tgl_bayar', 'transaksi_jmlhbayardenda', 'status_bayar']
    list_display = data
    list_display_links = data
    search_fields = ['pengguna_nama', 'subjenispajak_nama', 'objek_nama', 'tgl_bayar']
    list_filter = ['subjenispajak_nama','tahun','bulan']
