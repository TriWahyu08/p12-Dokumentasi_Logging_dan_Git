from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging # <-- DITAMBAHKAN

# --- INISIALISASI LOGGING (Langkah 2) ---
# Konfigurasi dasar: Semua log level INFO ke atas akan ditampilkan
# Format: Waktu - Level - Nama Kelas/Fungsi - Pesan
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

# Tambahkan logger untuk kelas yang akan kita gunakan
LOGGER = logging.getLogger('checkout')

# Model Sederhana
@dataclass
class Order:
    customer_name: str
    total_price: float
    status: str = "open"

# --- KODE BURUK (SEBELUM REFACTOR) ---
# class OrderManager (Pelanggaran SRP, OCP, DIP)
# class ini Dibiarkan sebagai referensi saja, karena ia tidak akan dieksekusi di Program Utama.
class OrderManager:
    def process_checkout(self, order: Order, payment_method: str):
        print(f"Memulai checkout untuk {order.customer_name}...")


        # LOGIKA PEMBAYARAN (Pelanggaran DIP)
        if payment_method == "credit_card":
            # Logika detail implementasi hardcoded di sini
            print("Processing Credit Card...")
        elif payment_method == "bank_transfer":
            # Logika detail implementasi hardcoded di sini
            print("Processing Bank Transfer...")
        else:
            print("Metode tidak valid.")
            return False

        # LOGIKA NOTIFIKASI (Pelanggaran SRP)
        print(f"Mengirim notifikasi ke {order.customer_name}...")
        order.status = "paid"
        return True
    
# --- ABSTRAKSI (Kontrak untuk OCP/DIP) ---
class IPaymentProcessor(ABC):
    """Kontrak: Semua prosesor pembayaran harus punya method 'process'."""
    @abstractmethod
    def process(self, order: Order) -> bool:
        pass

class INotificationService(ABC):
    """Kontrak: Semua layanan notifikasi harus punya method 'send'."""
    @abstractmethod
    def send(self, order: Order):
        pass

# --- IMPLEMENTASI KONKRIT (Plug-in) ---
class CreditCardProcessor(IPaymentProcessor):
    def process(self, order: Order) -> bool:
        # Ganti print() dengan LOGGER.info()
        LOGGER.info(f"Payment: Memproses kartu kredit.")
        return True

class EmailNotifier(INotificationService):
    def send(self, order: Order):
        # Ganti print() dengan LOGGER.info()
        LOGGER.info(f"Notif: Mengirim mail konfirmasi ke {order.customer_name}.")

# --- KELAS KOORDINATOR (SRP & OCP) ---
# class Checkout (Mematuhi SRP: Hanya mengoordinasi checkout, OCP & DIP)
# Nama kelas diubah dari "Checkout" menjadi "CheckoutService"
class CheckoutService: # <-- NAMA KELAS DIUBAH
    # Dependency Inversion (DIP): Bergantung pada abstraksi, bukan konkrit
    def __init__(self, payment_processor: IPaymentProcessor, notifier: INotificationService):
        """Menginisialisasi CheckoutService dengan dependensi yang diperlukan.

        Args:
            payment_processor (IPaymentProcessor): Implementasi interface pembayaran.
            notifier (INotificationService): Implementasi interface notifikasi.
        """
        self.payment_processor = payment_processor
        self.notifier = notifier

    def run_checkout(self, order: Order) -> bool:
        """Menjalankan proses checkout dan memvalidasi pembayaran.

        Args:
            order (Order): Objek pesanan yang akan diproses.

        Returns:
            bool: True jika checkout sukses, False jika gagal.
        """
        # Logging alih-alih print() (Langkah 2)
        LOGGER.info(f"Memulai checkout untuk {order.customer_name}. Total: {order.total_price}")

        payment_success = self.payment_processor.process(order) # Delegasi 1

        if payment_success:
            order.status = "paid"
            self.notifier.send(order) # Delegasi 2
            # Ganti print() dengan LOGGER.info()
            LOGGER.info("Checkout Sukses. Status pesanan: PAID.") 
            return True
        else:
            # Gunakan level ERROR/WARNING untuk masalah (Langkah 2)
            LOGGER.error("Pembayaran gagal. Transaksi dibatalkan.")
            return False
    
    
# --- PROGRAM UTAMA ---

# 1. Setup Dependencies
andi_order = Order("Andi", 500000)
email_service = EmailNotifier()

# 1. Inject implementasi Credit Card
cc_processor = CreditCardProcessor()
# Menggunakan CheckoutService
checkout_cc = CheckoutService(payment_processor=cc_processor, notifier=email_service)
print("--- Skenario 1: Credit Card ---")
checkout_cc.run_checkout(andi_order)

# 2. Pembuktian OCP: Menambah Metode Pembayaran QRIS (Tanpa Mengubah Checkout)
class QrisProcessor(IPaymentProcessor):
    def process(self, order: Order) -> bool:
        # Ganti print() dengan LOGGER.info()
        LOGGER.info("Payment: Memproses QRIS.")
        return True

budi_order = Order("Budi", 100000)
qris_processor = QrisProcessor()

# Inject implementasi QRIS yang baru dibuat
# Menggunakan CheckoutService
checkout_qris = CheckoutService(payment_processor=qris_processor, notifier=email_service)
print("\n--- Skenario 2: Pembuktian OCP (QRIS) ---")
checkout_qris.run_checkout(budi_order)
