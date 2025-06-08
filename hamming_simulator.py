import tkinter as tk
from tkinter import messagebox

# Yardımcı Fonksiyonlar

""" Bu fonksiyon 'x' sayısının 2'nin kuvveti olup olmadığını kontrol eder. 
Örnek: 4 = 100, 3 = 011 → 100 & 011 = 000 → sonuç 0, bu yüzden (x & (x - 1)) == 0 ise 'x', 2'nin kuvvetidir denir.
Bu pozisyonlara parity bitleri yerleştirilir. """
def is_power_of_two(x):
    return x != 0 and (x & (x - 1)) == 0

""" 'parity_pos' -> hesaplanan parity bitinin pozisyonudur.
Diğer bitlerin pozisyonları ile parity_pos’un AND işlemi yapılır, eğer sonuç sıfırdan farklıysa bu bit parity bitine bağlıdır denir.
Bu bitler XOR işlemine alınarak parity değeri hesaplanır. """
def calculate_parity(bits, parity_pos):
    parity = 0
    for i in range(1, len(bits) + 1):
        if i & parity_pos and i != parity_pos:
            parity ^= int(bits[i - 1])
    return parity

# Verilen(girilen) veri uzunluğu için gerekli parity bit sayısını hesaplar (2^r >= m + r + 1)
def calculate_parity_bits(data_len):
    r = 0
    while (2 ** r) < (data_len + r + 1):
        r += 1
    return r

""" Girilen verinin içine parity bitleri yerleştir yani onlar için yer açar. 
Güçleri 2 olan pozisyonlara (1, 2, 4, 8, ...) '0' ekler, diğer pozisyonlara veriyi yerleştirir.
Ayrıca toplam uzunluğa +1 ekler çünkü SEC-DED için genel parite biti (overall parity) de eklenir. """
def insert_parity_bits(data):
    data = list(data)
    r = calculate_parity_bits(len(data))
    total_len = len(data) + r + 1  # +1 overall parity için
    result = []
    j = 0

    for i in range(1, total_len):
        if is_power_of_two(i):
            result.append('0')  # Parity bitleri başlangıçta 0
        else:
            result.append(data[j])
            j += 1
    return result

""" Parity bitlerinin gerçek değerlerini hesaplar ve ilgili yerlere yazar.
Her parity biti, ona bağlı bitlerle XOR işlemine göre hesaplanır.
Ayrıca, kodun başına genel (overall) parite biti eklenir.(SEC-DED için gereklidir) """
def set_parity_bits(encoded):
    parity_positions = [2 ** i for i in range(len(encoded)) if 2 ** i <= len(encoded)]
    
    for parity_pos in parity_positions:
        parity = calculate_parity(encoded, parity_pos)
        encoded[parity_pos - 1] = str(parity)

    """ Overall parity için: Tüm bitlerin toplamının 2'ye bölümünden kalanı hesaplar. (mod 2) 
    Eğer toplam çiftse -> parity = 0, tekse -> parity = 1 olur.
    Bu parity bitini en başa ekleriz ve böylece çift bit hatalarını algılayabiliriz. (düzeltemesek de tespit ederiz) """
    overall = sum(int(bit) for bit in encoded) % 2
    encoded.insert(0, str(overall))  # Overall parity en başa
    return encoded

""" Kullanıcıdan gelen verinin (8, 16 veya 32 bit) kodlanmasını sağlar.
Geçersiz giriş kontrolü yapar (yalnızca 0 ve 1 içermeli, uzunluk 8-16-32 bit olmalı).
Parity bitleri yerleştirir ve değerleri atar.
Kodlanmış veriyi ve hata durumunu döndürür. """
def hamming_encode(data):
    if not all(c in '01' for c in data):
        return None, "Veri sadece 0 ve 1 içermeli."
    if len(data) not in (8, 16, 32):
        return None, "Sadece 8, 16, 32 bit veri girişi yapılabilir."

    encoded = insert_parity_bits(data)
    encoded = set_parity_bits(encoded)
    return ''.join(encoded), None

""" Kodlanmış veri üzerinde belirli bir bit pozisyonunda (kullanıcı seçer) yapay hata oluşturur yani
belirtilen pozisyondaki biti tersine çevirir. (0 → 1, 1 → 0) """
def introduce_error(codeword, position):
    if position < 0 or position >= len(codeword):
        return None
    flipped = '0' if codeword[position] == '1' else '1'
    return codeword[:position] + flipped + codeword[position+1:]

""" Kodlanmış verideki hataları tespit eder ve gerekirse düzeltir.
1. Bit: Genel parite (overall parity) biti → SEC-DED özelliğidir.
2. Parity bitleri ile sendrom kelimesini hesaplar ve hatalı bit pozisyonunu belirler.
3. Sendrom sıfır ama genel parite hatalıysa → çift bit hatası (düzeltilemez).
4. Sendrom sıfır değil, genel parite doğruysa → çift bit hatası (düzeltilemez)
5. Sendrom sıfır değil ve genel parite de hatalıysa → tek bit hatası → düzelt. """
def detect_and_correct(codeword):
    bits = list(codeword)
    if len(bits) < 2:
        return codeword, "Kod çok kısa."

    overall_parity = int(bits[0])
    bits = bits[1:]
    n = len(bits)
    syndrome = 0

    for i in range(n):
        pos = i + 1
        if is_power_of_two(pos):
            parity = calculate_parity(bits, pos)
            if parity != int(bits[i]):
                syndrome += pos

    recalculated_overall = sum(int(b) for b in bits) % 2

    if syndrome == 0 and recalculated_overall == overall_parity:
        return codeword, "Hata yok."
    elif syndrome != 0 and recalculated_overall != overall_parity:
        # Tek bit hatası var, düzeltilir
        if syndrome <= n:
            bits[syndrome - 1] = '0' if bits[syndrome - 1] == '1' else '1'
            corrected_code = str(sum(int(b) for b in bits) % 2) + ''.join(bits)
            return corrected_code, f"{syndrome}. bit düzeltildi."
        else:
            return codeword, "Geçersiz hata pozisyonu."
    else:
        # İki bit hata tespit edildi, düzeltilemez mesajı
        return codeword, "İki bit hatası tespit edildi, düzeltilemez."

# GUI 

# Veri girişinden alınan binary veriyi Hamming kodu ile kodlar ve kodlanmış veriyi arayüze yazdırır.
def encode_button_clicked():
    data = data_entry.get().strip()
    encoded, error = hamming_encode(data)
    if error:
        messagebox.showerror("Hata", error)
    else:
        encoded_var.set(encoded)
        corrected_var.set("")
        status_var.set("Kodlama başarılı.")

# Kullanıcının girdiği pozisyonda kodlanmış veriye yapay bir hata uygular ve hatalı veriyi arayüze günceller.
def error_button_clicked():
    code = encoded_var.get()
    try:
        pos = int(error_pos_entry.get())
    except ValueError:
        messagebox.showerror("Hata", "Hatalı bit pozisyonu girilmedi veya geçersiz.")
        return
    if pos < 0 or pos >= len(code):
        messagebox.showerror("Hata", f"Pozisyon 0 ile {len(code)-1} arasında olmalı.")
        return

    corrupted = introduce_error(code, pos)
    if corrupted is None:
        messagebox.showerror("Hata", "Hata oluşturulamadı.")
        return

    encoded_var.set(corrupted)
    status_var.set(f"{pos}. bit yapay olarak bozuldu.")
    corrected_var.set("")

""" Kodlanmış verideki hatayı kontrol eder; tek bit hatası varsa düzeltir, çift bit hatası varsa tespit eder ama düzeltemez.
Düzeltme sonrası sonucu ve mesajı arayüze yansıtır. """
def correct_button_clicked():
    code = encoded_var.get()
    if not code or not all(c in '01' for c in code):
        messagebox.showerror("Hata", "Kodlanmış veri eksik veya hatalı.")
        return

    corrected, message = detect_and_correct(code)
    corrected_var.set(corrected)
    status_var.set(message if message else "Durum mesajı üretilemedi.")

# Tkinter arayüzü

""" Tkinter ile GUI penceresi ve giriş/çıkış alanları tanımlanır:
- Veri girişi alanı
- Kodlanmış veri alanı
- Hatalı bit pozisyonu alanı
- Butonlar: Kodla, Hata Oluştur, Düzelt
- Çıktılar: Düzeltilmiş veri, durum mesajı  """

# Ana pencereyi oluşturur
window = tk.Tk()
window.title("Hamming SEC-DED Simülatörü")

""" tk.Label(...), tk.Entry(...), tk.Button(...) : Arayüzde kullanılan metin etiketleri, giriş kutuları ve butonlardır.
Her biri grid layout ile yerleştirilmiştir. """
tk.Label(window, text="Veri Girişi (8, 16, 32 bit):").grid(row=0, column=0, sticky="e")
data_entry = tk.Entry(window, width=40)
data_entry.grid(row=0, column=1)

tk.Button(window, text="Kodla", command=encode_button_clicked).grid(row=0, column=2)

tk.Label(window, text="Kodlanmış Veri:").grid(row=1, column=0, sticky="e")
encoded_var = tk.StringVar()
tk.Entry(window, textvariable=encoded_var, width=40).grid(row=1, column=1)

tk.Label(window, text="Hatalı Bit Pozisyonu (0 tabanlı):").grid(row=2, column=0, sticky="e")
error_pos_entry = tk.Entry(window, width=10)
error_pos_entry.grid(row=2, column=1, sticky="w")

tk.Button(window, text="Hata Oluştur", command=error_button_clicked).grid(row=2, column=2)

tk.Button(window, text="Düzelt", command=correct_button_clicked).grid(row=3, column=2)
tk.Label(window, text="Düzeltilmiş Veri:").grid(row=3, column=0, sticky="e")
corrected_var = tk.StringVar()
tk.Entry(window, textvariable=corrected_var, width=40).grid(row=3, column=1)

status_var = tk.StringVar()
tk.Label(window, textvariable=status_var, fg="blue").grid(row=4, column=0, columnspan=3)

""" Tkinter uygulamasını başlatır ve kullanıcı etkileşimini beklemeye alır.
Bu satır çalıştırılmadan GUI görünmez. Kullanıcı arayüzü açık kaldığı sürece olayları dinler. (örneğin butona tıklama) """
window.mainloop()
