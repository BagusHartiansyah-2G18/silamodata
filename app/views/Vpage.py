from django.shortcuts import render
from app.models import TransaksiPajak,TargetPajak
from django.contrib.auth.decorators import login_required

import pandas as pd

import urllib, base64
import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import plot
from plotly.subplots import make_subplots


import re
from collections import defaultdict

from app.views.sf.SFdata import Dtransaksi,dataFrameToJson

# mobil_saya = Mobil("Toyota", "Merah")
# mobil_saya.info()  # 


@login_required
def dashboard(request): 
    # http://localhost:8000/admin/app/transaksipajak/
    _ = Dtransaksi() 
    datax = _.daftarPajakPerbulan()
    config_pajak = {
        'kolom1': 'pajak',
        'kolom2': 'jumlah_data',
        'label1': 'Pajak',
        'label2': 'Jumlah Transaksi',
        'judul': 'Grafik Pajak dan Jumlah Transaksi per Bulan',
        'warna1': 'sunset',         # ✅ valid skema warna
        'warna2': 'Oranges'        # ✅ valid skema warna
    }

    config_denda = {
        'kolom1': 'denda',
        'kolom2': 'jumlah_berdenda',
        'label1': 'Denda',
        'label2': 'Pengusaha',
        'judul': 'Grafik Denda dan Jumlah Berdenda per Bulan',
        'warna1': 'Reds',          # ✅ valid skema warna
        'warna2': 'Greens'         # ✅ valid skema warna
    }



    chart_pajak = grafik_plotly_express_duo(datax, config_pajak)
    chart_denda = grafik_plotly_express_duo(datax, config_denda)

    
    hasil = _.groupBykecamatan()
    configKec = {
        "kolom1": "total_objek",
        "kolom2": "total_pajak",
        "label1": "Jumlah Objek",
        "label2": "Pajak",
        "judul": "Jumlah Objek & Pajak per Kecamatan",
        "warna1": "icefire"
    }

    grafik_kec = grafik_plotly_express_duo(hasil, configKec)
    tot =  _.pengusaha()


    configJenis = {
        "kolom1": "pajak",
        "kolom2": "jenis",
        "label1": "pajak",
        "label2": "Jenis",
        "judul": "Informasi Sumber Data PAD ("+"{:,.0f}".format(_.totalPajak())+")",
        "warna1": px.colors.qualitative.Pastel,  # opsional
        "hole": 0.3  # donut chart
    }

    grafikJenis = grafik_plotly_PIE(_.jenisPAD(),configJenis)
    context = {
        'chart_pajak': chart_pajak,
        'chart_denda': chart_denda,
        'grafik_kec':grafik_kec,
        # 'jenisPad':dataFrameToJson(_.jenisPAD()),
        'grafik_jenis':grafikJenis,
        'total_pajak':"{:,.0f}".format(_.totalPajak()),
        'total_omzet': "{:,.0f}".format(_.totalOmzet()),
        'tobjek': "{:,.0f}".format(len(tot)),
        'ttransaksi': "{:,.0f}".format(_.count()),
        "tgl":_.dataUpdate,
    }
    return render(request, 'dashboard.html', context)

@login_required
def user(request):
    _ = Dtransaksi()
    data = TransaksiPajak.objects.all()
    total_pajak = sum([d.pajak for d in data])
    total_omzet = sum([d.omzet_makanan + d.omzet_minuman for d in data])
    rasio = total_pajak / total_omzet if total_omzet else 0
    # print(user)
    return render(request, "user.html", {
        "total_pajak": total_pajak,
        "rasio": f"{rasio:.2%}",
        "data": data
    })

@login_required
def data(request):
    context = {
        # 'data': data,
    }
    return render(request, 'Ddata.html', context)

@login_required
def pengusaha(request):
    _ = Dtransaksi()
    data = dataFrameToJson(_.pengusaha())
    context = {
        'data': data,
    }
    return render(request, 'Dpengusaha.html', context)

@login_required
def wilaya(request):
    _ = Dtransaksi()
    data = dataFrameToJson(_.groupBykecamatan())
    context = {
        'data': data,
    }
    return render(request, 'Dwilaya.html', context)

@login_required
def denda(request):
    _ = Dtransaksi()
    data = dataFrameToJson(_.pengusahaBerdenda())
    context = {
        'data': data,
    }
    return render(request, 'Ddenda.html', context)

@login_required
def monitoring(request):
    
    _ = Dtransaksi()
    df_jenis = _.jenisPAD()

    # Ambil data TargetPajak dari database
    qs = TargetPajak.objects.all().values(
        'subjenispajak_id', 'subjenispajak_nama', 'target_tahun', 'target_nominal', 'target_id'
    )
    df_target = pd.DataFrame(list(qs))

    # Normalisasi nama pajak agar seragam
    df_jenis['jenis'] = df_jenis['jenis'].str.strip().str.lower()
    df_target['subjenispajak_nama'] = df_target['subjenispajak_nama'].str.strip().str.lower()
    df_target['target_nominal'] = df_target['target_nominal'].astype(float)
    # Merge berdasarkan nama pajak
    df_combined = pd.merge(
        df_jenis,
        df_target[['subjenispajak_nama','target_tahun','target_nominal']],
        left_on='jenis',
        right_on='subjenispajak_nama',
        how='left'
    )

    # df_combined['target_nominal'] = df_combined['target_nominal'].astype(float)
    df_combined['persentase'] = (df_combined['pajak'] / df_combined['target_nominal']) * 100
    # Preview hasil gabungan
    # print(df_combined.head(10))
    # selisih antara realisasi pajak dengan target nominal,
    df_combined['gap'] = df_combined['target_nominal'] - df_combined['pajak']



    # print(df_combined)
    context = {
        'data': dataFrameToJson(df_combined),
    }
    return render(request, 'Dmonitor.html', context)

# batas 
def grafik_plotly_express_duo(df, config):
    """
    df: DataFrame dengan kolom 'periode', kolom1, kolom2
    config: dict dengan key:
        - 'kolom1': nama kolom utama (nilai batang)
        - 'kolom2': nama kolom label tambahan
        - 'label1': label untuk kolom utama
        - 'label2': label untuk label tambahan
        - 'judul': judul grafik
        - 'warna1': skema warna batang
    """
    df['periode'] = df['periode'].astype(str)

    # Format label tambahan
    df['label_text'] = df[config['kolom2']].apply(lambda v: f"{v:,} {config['label2']}")

    fig = px.bar(
        df,
        x='periode',
        y=config['kolom1'],
        title=config['judul'],
        labels={'periode': 'Periode', config['kolom1']: config['label1']},
        text='label_text',
        color=config['kolom1'],
        color_continuous_scale=config.get('warna1', 'Blues')
    )

    fig.update_traces(textposition='outside', texttemplate='%{text}')
    fig.update_layout(xaxis_tickangle=-45)

    return plot(fig, output_type='div')

def grafik_plotly_PIE(df, config):
    """
    df: DataFrame dengan kolom 'periode', kolom1, kolom2
    config: dict dengan key:
        - 'kolom1': nama kolom utama (nilai numerik)
        - 'kolom2': nama kolom label tambahan (kategori)
        - 'label1': label untuk kolom utama
        - 'label2': label untuk label tambahan
        - 'judul': judul grafik
        - 'warna1': skema warna (opsional)
    """
    # Format label tambahan
    df['label_text'] = df[config['kolom1']].apply(lambda v: f"{v:,} {config['label1']}")

    # fig = px.pie(
    #     df,
    #     names=config['kolom2'],       # kategori
    #     values=config['kolom1'],      # nilai numerik
    #     title=config['judul'],
    #     color=config['kolom2'],       # warna berdasarkan kategori
    #     color_discrete_sequence=px.colors.qualitative.Set3
    #         if not config.get('warna1') else config['warna1'],
    #     hole=config.get('hole', 0)    # donut chart jika hole > 0
    # )
    # fig.update_traces(textinfo="percent+label", text=df['label_text'])

    # batas 
    
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.6, 0.4],   # proporsi kiri-kanan
        specs=[[{"type":"pie"}, {"type":"table"}]],
        subplot_titles=[]  # harus list, bukan string config['judul'], ""
    )

    # Pie chart di kiri dengan palet warna bagus
    fig.add_trace(
        go.Pie(
            labels=df[config['kolom2']],
            values=df[config['kolom1']],
            textinfo="percent+label",
            hole=config.get("hole", 0),
            marker=dict(colors=px.colors.qualitative.Set3)  # palet warna lembut
        ),
        row=1, col=1
    )

    # Info tambahan di kanan (tabel)
    # fig.add_trace(
    #     go.Table(
    #         header=dict(
    #             values=[config['label2'], config['label1']],
    #             fill_color='lightgrey',
    #             font=dict(color='black', size=12)
    #         ),
    #         cells=dict(
    #             values=[df[config['kolom2']], df[config['kolom1']]],
    #             fill_color='white',
    #             font=dict(color='darkblue', size=11)
    #         )
    #     ),
    #     row=1, col=2
    # )

    fig.update_layout(
        title_text=config['judul'],
        margin=dict(t=80, l=50, r=50, b=50)
    )


    return plot(fig, output_type='div')
def safe_number(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
