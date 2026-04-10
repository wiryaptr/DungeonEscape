# Dungeon Escape
Pembuatan game dengan mengimplementasikan Pemrograman Berbasis Objek menggunakan Bahasa Pemrograman Python yang berjudul "DUNGEON ESCAPE" Sebagai tugas UTS Matakuliah Pemrograman Berbasis Objek

---

# 🗝️ Dungeon Escape

**Dungeon Escape** adalah sebuah game *top-down 2D adventure* sederhana yang dibangun menggunakan library **Pygame**. Pemain harus menavigasi labirin yang berbahaya, mengumpulkan kunci, dan menghindari musuh untuk bisa melarikan diri ke level berikutnya.

## 🌟 Fitur Utama
* **Multi-Level System:** Memiliki sistem stage yang dapat ditingkatkan (Level 1 & Level 2).
* **Collision Physics:** Sistem deteksi tabrakan yang akurat antara pemain, dinding, musuh, dan item.
* **Dynamic UI:** Menampilkan status nyawa (HP), jumlah kunci yang dikumpulkan, dan level saat ini secara *real-time*.
* **Audio System:** Dilengkapi dengan musik latar (BGM) dan efek suara (SFX) untuk aksi mengambil kunci, terkena musuh, dan menang.
* **State Management:** Memiliki layar Menu Utama, layar Transisi Stage, dan layar Game Over.

## 🎮 Cara Bermain
1.  **Tujuan:** Kumpulkan minimal **3 Kunci** di setiap level untuk membuka pintu keluar (pintu cokelat).
2.  **Kontrol:** * `PANAH ATAS / BAWAH / KIRI / KANAN` untuk bergerak.
    * `SPACE` untuk memulai game dari Menu.
    * `ENTER` untuk melanjutkan ke stage berikutnya setelah menang.
    * `R` untuk restart jika kamu kalah atau ingin mengulang permainan.
3.  **Hambatan:** Jangan biarkan HP kamu mencapai 0! Musuh akan berpatroli dan mengurangi nyawa jika bersentuhan.

## 🛠️ Persyaratan Sistem
Pastikan kamu sudah menginstal Python dan library Pygame di komputermu:

```bash
pip install pygame
```

## 📂 Struktur Aset
Untuk menjalankan game dengan fitur penuh, pastikan file-file berikut berada dalam folder yang sama dengan skrip Python:

* **Gambar:** `player.png`, `enemy.png`, `key.png`, `pintu.png`.
* **Audio:** `musik_tema.mp3`, `dapat_kunci.mp3`, `kena_musuh.mp3`, `menang.mp3`.

> *Catatan: Jika aset tidak ditemukan, game akan tetap berjalan menggunakan warna cadangan (Solid Color).*
