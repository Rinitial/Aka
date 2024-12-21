# Import pustaka yang dibutuhkan
import tkinter as tk  # Untuk membuat antarmuka GUI
from tkinter import messagebox  # Untuk menampilkan kotak pesan di GUI
import mysql.connector  # Untuk menghubungkan ke database MySQL
import time  # Untuk menghitung waktu eksekusi pencarian
import matplotlib.pyplot as plt  # Untuk membuat grafik
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Untuk menampilkan grafik di tkinter

# Konfigurasi koneksi ke database
config = {
    'user': 'root',          # Nama pengguna MySQL
    'password': '',          # Kata sandi MySQL (kosong dalam konfigurasi lokal)
    'host': 'localhost',     # Alamat server MySQL
    'database': 'aka',       # Nama database yang digunakan
    'port': 3306             # Port default MySQL
}

# Fungsi untuk mengambil data merek (Brand) dari tabel 'ramen'
def fetch_brands():
    try:
        connection = mysql.connector.connect(**config)  # Membuat koneksi ke database
        cursor = connection.cursor()  # Membuat objek cursor untuk menjalankan query SQL
        cursor.execute("SELECT Brand FROM ramen")  # Mengambil semua merek dari tabel 'ramen'
        brands = [row[0] for row in cursor.fetchall()]  # Mengambil hasil query dalam bentuk list
        return brands  # Mengembalikan list merek
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")  # Menampilkan pesan kesalahan database
        return []  # Mengembalikan list kosong jika ada kesalahan
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()  # Menutup cursor
            connection.close()  # Menutup koneksi database

# Fungsi pencarian sekuensial rekursif
def recursive_search(brands, target, index=0):
    time.sleep(0.05)  # Memberi jeda waktu untuk mensimulasikan pencarian
    if index >= len(brands):  # Basis rekursi: jika indeks melebihi panjang list
        return False
    if brands[index] == target:  # Jika merek ditemukan pada indeks saat ini
        return True
    return recursive_search(brands, target, index + 1)  # Rekursi ke indeks berikutnya

# Fungsi pencarian sekuensial iteratif
def iterative_search(brands, target):
    time.sleep(0.05)  # Memberi jeda waktu untuk mensimulasikan pencarian
    for brand in brands:  # Iterasi melalui setiap elemen dalam list
        if brand == target:  # Jika merek ditemukan
            return True
    return False  # Jika tidak ditemukan setelah semua iterasi

# Fungsi untuk menampilkan grafik perbandingan waktu pencarian di UI
def plot_line_chart_on_ui(recursive_times, iterative_times):
    fig, ax = plt.subplots(figsize=(8, 6))  # Membuat figur grafik dengan ukuran 8x6 inci
    ax.plot(range(1, len(recursive_times) + 1), recursive_times, 
            label="Recursive Search", color='red', marker='o')  # Garis merah untuk pencarian rekursif
    ax.plot(range(1, len(iterative_times) + 1), iterative_times, 
            label="Iterative Search", color='blue', marker='o')  # Garis biru untuk pencarian iteratif

    # Menambahkan label sumbu dan judul grafik
    ax.set_xlabel('Search #')
    ax.set_ylabel('Time (seconds)')
    ax.set_title('Recursive vs Iterative Search Time')
    ax.legend()  # Menambahkan legenda grafik
    ax.grid(True)  # Menambahkan grid ke grafik

    # Menyematkan grafik ke dalam antarmuka tkinter
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Fungsi yang menangani aksi ketika tombol pencarian ditekan
def handle_search(search_type):
    brand_name = product_input.get()  # Mengambil input dari kotak teks
    if not brand_name:
        messagebox.showwarning("Input Error", "Please enter a brand name.")  # Peringatan jika input kosong
        return

    brands = fetch_brands()  # Mengambil daftar merek dari database
    if not brands:
        messagebox.showerror("Data Error", "No brands found in the database.")  # Peringatan jika daftar kosong
        return

    global recursive_times, iterative_times  # Variabel global untuk menyimpan waktu pencarian

    if search_type == "recursive":
        recursive_times = []
        for i in range(10):  # Melakukan pencarian rekursif sebanyak 10 kali
            start_time = time.time()
            recursive_search(brands, brand_name)
            elapsed_time = time.time() - start_time
            recursive_times.append(elapsed_time)

        avg_time = sum(recursive_times) / len(recursive_times)  # Menghitung rata-rata waktu rekursif
        time_output.delete(0, tk.END)
        time_output.insert(0, f"{avg_time:.6f} seconds")  # Menampilkan rata-rata di kotak teks

        messagebox.showinfo("Search Result", 
                            f"Recursive Search completed for '{brand_name}'.\nAverage Time: {avg_time:.6f}s")

    elif search_type == "iterative":
        iterative_times = []
        for i in range(10):  # Melakukan pencarian iteratif sebanyak 10 kali
            start_time = time.time()
            iterative_search(brands, brand_name)
            elapsed_time = time.time() - start_time
            iterative_times.append(elapsed_time)

        avg_time = sum(iterative_times) / len(iterative_times)  # Menghitung rata-rata waktu iteratif
        time_output.delete(0, tk.END)
        time_output.insert(0, f"{avg_time:.6f} seconds")  # Menampilkan rata-rata di kotak teks

        messagebox.showinfo("Search Result", 
                            f"Iterative Search completed for '{brand_name}'.\nAverage Time: {avg_time:.6f}s")

    plot_line_chart_on_ui(recursive_times, iterative_times)  # Memperbarui grafik dengan data terbaru

# Pengaturan UI utama
root = tk.Tk()
root.title("Sequential Search UI")  # Judul jendela aplikasi
root.geometry("900x800")  # Ukuran jendela
root.resizable(False, False)  # Jendela tidak dapat diubah ukurannya

# Label dan input untuk nama merek
tk.Label(root, text="Brand Name:").grid(row=0, column=0, padx=10, pady=10)
product_input = tk.Entry(root, width=30)
product_input.grid(row=0, column=1, padx=10, pady=10)

# Label dan input untuk waktu pencarian
tk.Label(root, text="Running Time:").grid(row=1, column=0, padx=10, pady=10)
time_output = tk.Entry(root, width=30)
time_output.grid(row=1, column=1, padx=10, pady=10)

# Tombol untuk pencarian rekursif dan iteratif
recursive_btn = tk.Button(root, text="Recursive Search", command=lambda: handle_search("recursive"))
recursive_btn.grid(row=2, column=0, padx=10, pady=20)

iterative_btn = tk.Button(root, text="Iterative Search", command=lambda: handle_search("iterative"))
iterative_btn.grid(row=2, column=1, padx=10, pady=20)

# Frame untuk grafik
graph_frame = tk.Frame(root)
graph_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=20)

# Menjalankan aplikasi tkinter
root.mainloop()
