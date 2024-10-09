# Jogjappetite
## Anggota Kelompok C11
- [Dinda Dinanti ](https://github.com/dinan26)(2306245440)
- [Irfan Rizqi Nurrahman ](https://github.com/irfanrizqinr)(2306216724)
- [Sulthan Adrin Pasha Siregar](https://github.com/sulthanadrin) (2306201306)
- [Naira Shafiqa Afiany](https://github.com/nairafiany) (2306240124)
- [Filbert Aurelian Tjiaranata](https://github.com/FilbertAT) (2306152336)

## Deskripsi Aplikasi
Jogjappetite adalah platform yang dirancang untuk mempermudah pengguna dalam menemukan, menilai, dan mengulas tempat makan di Yogyakarta. Pengguna dapat menjelajahi berbagai restoran, memberikan ulasan, dan menambahkan tempat makan baru yang belum tersedia di aplikasi. Dengan fitur interaktif seperti explore restaurant, wishlist restaurant, dan fitur pencarian yang canggih, Jogjappetite memastikan penggunanya selalu terhubung dengan tren kuliner terbaru di Jogja. Aplikasi ini mengutamakan fleksibilitas dalam pencarian restoran melalui filter yang dapat disesuaikan dengan kebutuhan pengguna.

## Daftar Modul Aplikasi dan Penjelasannya
### Explore Restaurant
**Dikerjakan oleh Sultan Adrin Pasha Siregar**

Pengguna dapat menjelajahi restoran-restoran yang tersedia di Jogjappetite berdasarkan berbagai kategori seperti jenis makanan, lokasi, popularitas, serta filter tambahan. Kategori ini juga mencakup clustering kuliner untuk berbagai wilayah, misalnya:

* Makanan Tradisional Jogja
* Western Food di Jogja
* Indonesian Food di Jogja
* Restoran dengan View
* Restoran yang Comfy untuk Kerja
* Restoran Halal dan Non-Halal

### Wishlist Restaurant
**Dikerjakan oleh Irfan Rizqi Nurrahman**

Pengguna dapat membuat wishlist yang berisi tempat-tempat makan yang mereka minati, disimpan untuk referensi masa mendatang. Wishlist ini bisa di-filter berdasarkan kategori yang disediakan, misalnya ingin mengunjungi restoran dengan view indah atau tempat makan halal.

### Rate Restaurants
**Dikerjakan oleh Naira Shafiqa Afiany**

Modul ini memungkinkan pengguna untuk memberikan rating dan ulasan terhadap restoran yang sudah mereka kunjungi. Pengguna bisa memberikan penilaian berdasarkan berbagai aspek seperti rasa makanan, kebersihan, suasana, dan harga. Selain itu, setiap restoran akan menampilkan overview yang mencakup informasi penting seperti lokasi, menu utama, dan kategori jenis makanan (cuisine), seperti makanan tradisional, Western, atau lainnya. Modul ini juga mendukung fitur balasan (reply) pada ulasan, di mana pengguna dapat berdiskusi lebih lanjut tentang pengalaman mereka. Misalnya, pengguna dapat menanyakan rekomendasi menu, memberikan saran, atau berbagi pengalaman pribadi.

### Search Restaurant
**Dikerjakan oleh Filbert Aurelian Tjiaranata**

Modul pencarian ini memungkinkan pengguna untuk menemukan restoran berdasarkan kata kunci tertentu. Walaupun pengguna mungkin melakukan kesalahan kecil dalam pengetikan (typo), fitur ini tetap bisa mendeteksi dan menampilkan hasil yang relevan. Pengguna juga dapat memfilter hasil pencarian berdasarkan kategori seperti makanan tradisional, restoran halal, atau tempat makan yang nyaman untuk bekerja, sehingga mempermudah dalam menemukan restoran yang sesuai dengan preferensi.

### Add Restaurant For Restaurant Owner
**Dikerjakan oleh Dinda Dinanti**

Modul ini memberi kemampuan kepada pemilik restoran untuk menambahkan restoran baru ke platform yang mungkin belum terdaftar. Pemilik restoran juga dapat menghapus restorannya dari daftar jika diperlukan. Selain itu, pemilik dapat melihat statistik seperti berapa banyak pengguna yang menambahkan restoran mereka ke wishlist atau berapa banyak rating dan ulasan yang sudah diberikan.


## Sumber Dataset
Platform ini dapat memanfaatkan dataset seperti yang tersedia di Kaggle - Places to Eat in Jogja Region, yang mencakup 291 restoran di wilayah Jogja. Selain itu, pengguna dengan role restaurant owners bisa menambah data restoran baru untuk menjaga agar database selalu up-to-date.

[Kaggle - Places to Eat in Jogja Region](https://www.kaggle.com/datasets/yudhaislamisulistya/places-to-eat-in-the-jogja-region?resource=download)

## Jenis Pengguna (Role)
Pada aplikasi kami, terdapat tiga jenis penggunanya, yaitu:
* User (guest) : 
Dapat melihat restoran, membaca ulasan, dan melihat wishlist tanpa perlu login.

* Logged in User (member) : 
Pengguna yang terdaftar dapat membuat ratings dan menambahkan restoran ke wishlist.

* Restaurant Owner :
Pemilik restoran yang akan membuat dan menghapus restoran yang ada pada list restoran yang tersedia. Pemilik restoran juga dapat melihat statistik restoran yang dimilikinya (seperti jumlah pengguna yang menambahkan restoran miliknya pada wishlist mereka)

## Tautan Deployment Aplikasi
http://naira-shafiqa-jogjappetite.pbp.cs.ui.ac.id/