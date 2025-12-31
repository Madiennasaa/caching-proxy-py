# Caching Proxy Server (Python)

Proyek ini mengimplementasikan *caching proxy server* sederhana yang dibangun menggunakan Python. Server ini bertindak sebagai perantara yang meneruskan permintaan HTTP ke server asal (*origin server*) dan menyimpan (*cache*) responsnya.

Jika permintaan yang sama diterima lagi, server akan mengembalikan data dari *cache* alih-alih menghubungi server asal, sehingga mempercepat waktu respons.

Server juga menambahkan header `X-Cache` pada setiap respons untuk mengindikasikan status *cache*.

(https://roadmap.sh/projects/caching-server)

## 🚀 Fitur

* **Forwarding Permintaan:** Meneruskan permintaan ke *origin server* yang ditentukan.
* **Response Caching:** Menyimpan respons `GET` dengan status kode 200 (OK).
* **Header `X-Cache`:** Menambahkan header `X-Cache: HIT` (dari cache) atau `X-Cache: MISS` (dari origin server).
* **CLI Utility:** Mendukung mode menjalankan server dan mode membersihkan cache.

## 🛠️ Instalasi

Pastikan Anda memiliki Python 3 terinstal. Proyek ini membutuhkan pustaka `requests`.

1.  **Kloning Repository (atau unduh file):**
    ```bash
    git clone [https://github.com/Madiennasaa/caching-proxy-py.git](https://github.com/Madiennasaa/caching-proxy-py.git)
    cd caching-proxy-py
    ```

2.  **Instal Dependensi:**
    ```bash
    pip install requests
    ```

## ⚙️ Cara Menjalankan

Server dapat dijalankan dalam dua mode: mode server dan mode pembersihan cache.

### 1. Menjalankan Server Proxy

Gunakan argumen `--port` untuk port lokal dan `--origin` untuk URL server asal (contoh ini menggunakan `http://dummyjson.com`).

```bash
python caching_proxy.py --port 3000 --origin [http://dummyjson.com](http://dummyjson.com)