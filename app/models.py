from django.db import models
class SimtaxSession(models.Model):
    cookies = models.JSONField(default=dict)
    note = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class PotensiEkonomi(models.Model):
    nama = models.CharField(max_length=200)
    deskripsi = models.TextField()
    lokasi = models.CharField(max_length=200)
    sektor = models.CharField(max_length=100, choices=[
        ('pertanian', 'Pertanian'),
        ('pariwisata', 'Pariwisata'),
        ('industri', 'Industri'),
        ('perdagangan', 'Perdagangan'),
        ('lainnya', 'Lainnya'),
    ])
    estimasi_nilai = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return self.nama

class TransaksiPajak(models.Model):
    bulan = models.CharField(max_length=2, null=True, blank=True)
    bulan_huruf = models.CharField(max_length=20, null=True, blank=True)
    tahun = models.IntegerField(null=True, blank=True)

    nopd = models.CharField(max_length=30, null=True, blank=True)
    npwpd = models.CharField(max_length=20, null=True, blank=True)
    wp_id = models.CharField(max_length=50, null=True, blank=True)

    objek_id = models.CharField(max_length=50, null=True, blank=True)
    objek_nama = models.CharField(max_length=100, null=True, blank=True)
    objek_alamat = models.TextField(null=True, blank=True)

    pengguna_nama = models.CharField(max_length=100, null=True, blank=True)
    subjenispajak_id = models.CharField(max_length=50, null=True, blank=True)
    subjenispajak_nama = models.CharField(max_length=100, null=True, blank=True)

    omzet_makanan = models.IntegerField(null=True, blank=True)
    omzet_minuman = models.IntegerField(null=True, blank=True)
    pajak = models.IntegerField(null=True, blank=True)
    status_bayar = models.BooleanField(null=True, blank=True)

    tgl_bayar = models.DateField(null=True, blank=True)
    tglbayar1 = models.DateTimeField(null=True, blank=True)
    tgl_entry = models.DateTimeField(null=True, blank=True)
    tgl_jatuh_tempo = models.DateField(null=True, blank=True)

    transaksi_jmlhbayardenda = models.IntegerField(null=True, blank=True)
    transaksi_jmlhdendapembayaran = models.IntegerField(null=True, blank=True)
    transaksi_kodebayarbank = models.CharField(max_length=50, null=True, blank=True)
    transaksi_kodeqris = models.TextField(null=True, blank=True)

    transaksi_masaawal = models.DateField(null=True, blank=True)
    transaksi_masaakhir = models.DateField(null=True, blank=True)
    transaksi_periodepajak = models.CharField(max_length=4, null=True, blank=True)

    transaksi_tglawalreklame = models.CharField(max_length=20, null=True, blank=True)
    transaksi_tglakhirreklame = models.CharField(max_length=20, null=True, blank=True)

    transaksi_propertis = models.JSONField(default=dict, null=True, blank=True)

    def rasio_pembayaran(self):
        total_omzet = (self.omzet_makanan or 0) + (self.omzet_minuman or 0)
        return self.pajak / total_omzet if total_omzet > 0 and self.pajak else 0


class SimtaxSession(models.Model):
    cookies = models.JSONField(default=dict)
    note = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class TargetPajak(models.Model):
    target_id = models.CharField(max_length=200, unique=True)
    subjenispajak_id = models.CharField(max_length=200)
    subjenispajak_nama = models.CharField(max_length=200)
    target_tahun = models.PositiveIntegerField()
    target_nominal = models.DecimalField(max_digits=20, decimal_places=2)

    # def __str__(self):
    #     return f"{self.subjenispajak_nama} - {self.target_tahun}"

class PotensiBaru(models.Model):
    id_potensi = models.AutoField(primary_key=True)
    nama_potensi = models.CharField(max_length=200)
    deskripsi_potensi = models.TextField(blank=True, null=True)
    perangkat_daerah_pengusul = models.CharField(max_length=150)
    lokasi = models.CharField(max_length=150, blank=True, null=True)
    kategori_sektor = models.CharField(max_length=100, blank=True, null=True)
    status_perda = models.BooleanField(default=False)  # True jika sudah diatur Perda
    nomor_perda_terkait = models.CharField(max_length=50, blank=True, null=True)
    tanggal_input = models.DateTimeField(auto_now_add=True)
    nilai_estimasi = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    status_verifikasi = models.BooleanField(default=False)
    catatan_analisis = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Potensi Baru"
        verbose_name_plural = "Potensi Baru"

    def __str__(self):
        return self.nama_potensi
