# Modify Game Brick Breaker

---

## 🎮 Deskripsi Proyek
Proyek ini merupakan modifikasi dan pengembangan tingkat lanjut dari game **Brick Breaker (Block Breaker)** menggunakan bahasa pemrograman **Python** dan library GUI **Pygame**. Game ini dirancang secara modular dengan menerapkan prinsip-prinsip dasar Pemrograman Berorientasi Objek (*Object-Oriented Programming - OOP*), seperti enkapsulasi (*encapsulation*), pewarisan (*inheritance*), pemisahan tanggung jawab kelas, serta abstraksi logika game.

---

## 🚀 Fitur Unggulan & Modifikasi

### 1. 🛸 Musuh Pesawat Alien (Inverted Triangle `▼`)
* **Class `Alien` & `AlienLaser`**: Musuh berbentuk pesawat segitiga terbalik yang berpatroli secara horizontal di bagian atas arena dengan animasi melayang (*bobbing effect*).
* **Mekanik Menyerang**: Alien menembakkan proyektil laser plasma ke arah bawah menuju paddle pemain.
* **Mekanik Hantaman & Reward**: Alien memiliki *Health Bar* dan dapat dihantam serta dihancurkan menggunakan bola pantul. Menghancurkan alien memberikan **+300 poin** dan **pasti menjatuhkan Power-Up langka**.

### 2. 🎲 Penempatan Balok Prosedural (Procedural Random Blocks)
* Formasi balok tidak statis, melainkan dihasilkan secara **acak namun simetris** di setiap level baru (*arcade-grade procedural generation*).
* Variasi balok:
  * 🧱 **Normal Block:** Balok warna-warni standar (1x hit).
  * ◆ **Armored Block:** Balok lapis baja yang membutuhkan 2x hit untuk pecah.
  * 💣 **Bomb Block:** Meledakkan balok-balok di sekitarnya saat hancur disertai efek guncangan layar (*screen shake*).
  * `$` **Gold Block:** Balok bernilai tinggi (150 poin) dan pasti menjatuhkan kapsul power-up.

### 3. 🎁 Sistem 5 Kapsul Power-Up
* Balok yang hancur memiliki peluang menjatuhkan kapsul item:
  * 🟢 **[W] WIDE PADDLE:** Memperlebar ukuran paddle sebesar 50% selama 10 detik. Berfungsi ganda sebagai perisai dari tembakan laser alien.
  * 🟣 **[M] MULTI-BALL:** Membelah setiap bola aktif menjadi 3 bola sekaligus.
  * ❤️ **[+] EXTRA LIFE:** Menambah 1 nyawa ekstra pemain.
  * ⚡ **[S] SLOW MOTION:** Memperlambat laju bola selama 8 detik untuk kontrol ekstra presisi.
  * 🔥 **[F] FIREBALL PIERCE:** Bola berubah menjadi bola api yang menembus deretan balok tanpa memantul balik selama 6 detik.

### 4. 🎯 Fisika Pantulan Dinamis & Kontrol Peluncuran
* **Dynamic Bounce Angle:** Arah pantulan bola ditentukan secara fleksibel berdasarkan titik benturan di paddle (-65° hingga +65°), memungkinkan pemain untuk membidik balok secara akurat.
* **Serve Mechanism:** Bola diawali dengan menempel di paddle dan diluncurkan dengan menekan tombol **`SPACE`**.

### 5. ✨ Visual & Audio Arcade
* **Visual Effects:** Sistem partikel serpihan balok (*debris*), jejak ekor komet bola (*comet trail*), floating score, dan combo multiplier counter.
* **Sound & BGM System:** 11 efek suara arcade berkualitas tinggi (44.1 kHz PCM) dan musik latar retro chiptune dengan shortcut Mute `[M]`.

---

## 🏛️ Struktur Arsitektur OOP

| Kelas / Modul | Tanggung Jawab / Peran |
|---|---|
| `Striker` | Mengelola posisi, lebar, kecepatan, render paddle, timer power-up, dan sistem perisai/kebal. |
| `Ball` | Mengelola posisi, vektor kecepatan `(xFac, yFac)`, pantulan dinamis, status stuck, dan trail komet. |
| `Block` | Mengelola koordinat, dimensi, tipe balok (normal/armored/bomb/gold), HP balok, dan render. |
| `Alien` | Mengelola musuh alien segitiga terbalik, patroli horizontal, cooldown tembakan, HP, dan render. |
| `AlienLaser` | Mengelola proyektil laser yang ditembakkan oleh musuh alien. |
| `PowerUp` | Mengelola item jatuh, tipe efek, deteksi tangkapan, dan render kapsul. |
| `Particle` | Mengelola simulasi partikel serpihan ledakan dengan gravitasi dan umur (*lifespan*). |
| `FloatingText` | Mengelola teks skor dan notifikasi yang melayang ke atas dengan efek fade-out. |
| `SoundManager` | Mengelola pemutaran SFX, BGM loop, kontrol volume, dan toggle mute. |

---

## ⌨️ Kontrol Permainan

* **Panah Kiri (`←`) / `A`** : Menggerakkan paddle ke kiri
* **Panah Kanan (`→`) / `D`** : Menggerakkan paddle ke kanan
* **`SPACE`** : Meluncurkan bola dari paddle / Restart ronde saat Game Over
* **`M`** : Toggle Suara (Mute / Unmute)
* **`ESC`** : Keluar dari game

---

## 💻 Cara Menjalankan

1. Pastikan Python 3 dan dependencies sudah terpasang:
   ```bash
   pip install pygame-ce
   ```
2. Jalankan program utama:
   ```bash
   python "Pertemuan 9.py"
   ```

