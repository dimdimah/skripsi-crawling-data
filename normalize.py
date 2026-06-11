def normalize(job, source):
    return {
        "nama_perusahaan": job.get("company"),
        "posisi_jabatan": job.get("title"),
        "deskripsi_kualifikasi": job.get("title"),
        "link_pendaftaran": job.get("url"),
        "sumber_data": source,
        "is_active": True
    }