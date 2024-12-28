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

# Inisialisasi variabel global
search_results = []  # Menyimpan hasil pencarian (index, brand, recursive_time, iterative_time)

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
    if index >= len(brands):
        return -1
    if brands[index] == target:
        return index
    return recursive_search(brands, target, index + 1)

# Fungsi pencarian sekuensial iteratif
def iterative_search(brands, target):
    index = 0
    while index < len(brands):
        if brands[index] == target:
            return True
        index += 1
    return False

# Fungsi untuk mengukur waktu pencarian dengan pengulangan
def benchmark_search(search_function, brands, target, iterations=1000):
    start_time = time.time()
    result = -1
    for _ in range(iterations):
        result = search_function(brands, target)
    end_time = time.time()
    return (end_time - start_time) / iterations, result  # Rata-rata waktu per iterasi dan indeks hasil

# Fungsi untuk memperbarui grafik perbandingan waktu pencarian di UI
def plot_line_chart_on_ui():
    for widget in graph_frame.winfo_children():
        widget.destroy()  # Menghapus grafik sebelumnya di dalam frame

    if not search_results:
        return  # Tidak ada data untuk ditampilkan

    fig, ax = plt.subplots(figsize=(8, 5))  # Mengatur ukuran grafik lebih kecil dibanding tampilan utama

    indexes = [result['index'] for result in search_results]
    recursive_times = [result['recursive_time'] for result in search_results]
    iterative_times = [result['iterative_time'] for result in search_results]

    ax.plot(indexes, recursive_times, label="Recursive Search", color='red', marker='o')
    ax.plot(indexes, iterative_times, label="Iterative Search", color='blue', marker='o')

    # Tambahkan nomor indeks data di bawah grafik (di sumbu x)
    ax.set_xticks(indexes)
    ax.set_xticklabels([str(result['position']) for result in search_results], rotation=45, fontsize=10)

    # Format sumbu Y dengan notasi ilmiah atau dengan 6 angka desimal
    ax.set_ylabel('Running Time (seconds)')
    ax.set_yticks([round(i, 6) for i in ax.get_yticks()])  # Format sumbu Y dalam 6 angka desimal
    ax.set_yticklabels([f'{i:.6f}' for i in ax.get_yticks()])  # Format angka menjadi 6 digit desimal

    ax.set_xlabel('Search Index (Position)')
    ax.set_title('Recursive vs Iterative Search Time')
    ax.legend()
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

    # Sinkronkan waktu pencarian terakhir dengan label
    last_result = search_results[-1]
    time_output.delete(0, tk.END)
    time_output.insert(0, f"Rec: {last_result['recursive_time']:.6f}s, Iter: {last_result['iterative_time']:.6f}s")

# Fungsi untuk menangani pencarian
def handle_search():
    brand_name = product_input.get()
    if not brand_name:
        messagebox.showwarning("Input Error", "Please enter a brand name.")
        return

    brands = fetch_brands()
    if not brands:
        messagebox.showerror("Data Error", "No brands found in the database.")
        return

    index = len(search_results) + 1

    iterations = 1000  # Jumlah pengulangan untuk benchmark

    # Rekursif
    recursive_time, recursive_position = benchmark_search(recursive_search, brands, brand_name, iterations)

    # Iteratif
    iterative_time, iterative_position = benchmark_search(iterative_search, brands, brand_name, iterations)

    # Simpan hasil
    search_results.append({
        'index': index,
        'brand': brand_name,
        'recursive_time': recursive_time,
        'iterative_time': iterative_time,
        'position': recursive_position if recursive_position != -1 else "Not Found"
    })

    # Tampilkan di GUI
    plot_line_chart_on_ui()  # Update grafik dan label
    messagebox.showinfo("Search Complete", f"Search completed for '{brand_name}' at position {recursive_position if recursive_position != -1 else 'Not Found'}.")

# Pengaturan UI utama
root = tk.Tk()
root.title("Sequential Search")
root.geometry("800x700")  # Memperbesar ukuran jendela agar grafik tampil penuh
root.resizable(False, False)

# Input untuk nama merek
tk.Label(root, text="Brand Name:").grid(row=0, column=0, padx=10, pady=10)
product_input = tk.Entry(root, width=30)
product_input.grid(row=0, column=1, padx=10, pady=10)

# Output untuk waktu pencarian
tk.Label(root, text="Running Time:").grid(row=1, column=0, padx=10, pady=10)
time_output = tk.Entry(root, width=30)
time_output.grid(row=1, column=1, padx=10, pady=10)

# Tombol pencarian
search_btn = tk.Button(root, text="Search", command=handle_search)
search_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=20)

# Frame untuk grafik
graph_frame = tk.Frame(root)
graph_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=15)

# Menjalankan aplikasi tkinter
root.mainloop()