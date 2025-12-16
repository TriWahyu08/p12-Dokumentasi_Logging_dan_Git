from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass
import logging # <-- DITAMBAHKAN

# --- INISIALISASI LOGGING (Persyaratan 2) ---
# Konfigurasi dasar: Semua log level INFO ke atas akan ditampilkan
# Format: Waktu - Level - Nama Kelas/Fungsi - Pesan
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

# Tambahkan logger untuk kelas yang akan kita gunakan
LOGGER = logging.getLogger('registration')

# Asumsi Model Data Mahasiswa dan Mata Kuliah
@dataclass
class Student:
    name: str
    current_sks: int
    prerequisites_met: bool
    # Daftar kode jadwal, misal ['Senin_08.00', 'Selasa_10.00']
    schedule: List[str] 

@dataclass
class Course:
    code: str
    sks: int
    prerequisite_needed: bool
    schedule_code: str

# ----------------------------------------------------
# 2. Implementasi DIP/OCP: Abstraksi dan Kelas Konkrit
# ----------------------------------------------------

class IValidationRule(ABC):
    """
    Abstraksi (Kontrak) untuk semua aturan validasi pendaftaran mahasiswa. 
    
    Mematuhi DIP (Dependency Inversion Principle) dan OCP (Open/Closed Principle).
    """
    @abstractmethod
    def validate(self, student: Student, course: Course) -> bool:
        """Mengimplementasikan logika validasi spesifik.

        Args:
            student (Student): Objek mahasiswa yang akan mendaftar.
            course (Course): Objek mata kuliah yang didaftarkan.

        Returns:
            bool: True jika valid, False jika gagal.
        """
        pass

class SksLimitRule(IValidationRule):
    """Kelas Konkrit untuk Validasi Batas SKS."""
    MAX_SKS = 24

    def validate(self, student: Student, course: Course) -> bool:
        """Memeriksa apakah penambahan SKS tidak melebihi batas MAX_SKS."""
        if student.current_sks + course.sks > self.MAX_SKS:
            # Mengganti print() dengan LOGGER.warning() (Persyaratan 2)
            LOGGER.warning(
                f"❌ GAGAL SKS: {student.name} melampaui batas SKS "
                f"({student.current_sks + course.sks} dari {self.MAX_SKS})."
            )
            return False
        return True

class PrerequisiteRule(IValidationRule):
    """Kelas Konkrit untuk Validasi Prasyarat."""
    def validate(self, student: Student, course: Course) -> bool:
        """Memeriksa apakah prasyarat mata kuliah telah dipenuhi."""
        if course.prerequisite_needed and not student.prerequisites_met:
            # Mengganti print() dengan LOGGER.warning() (Persyaratan 2)
            LOGGER.warning(
                f"❌ GAGAL PRASYARAT: {student.name} belum memenuhi prasyarat untuk {course.code}."
            )
            return False
        return True

# ----------------------------------------------------
# 3. Implementasi SRP: Kelas Koordinator
# ----------------------------------------------------

class RegistrationService:
    """
    Kelas Koordinator untuk proses pendaftaran mata kuliah.
    
    Hanya bertanggung jawab mengoordinasi dan menjalankan list validasi (Mematuhi SRP).
    """
    
    def __init__(self, validation_rules: List[IValidationRule]):
        """Menginisialisasi RegistrationService dengan list aturan validasi.

        Args:
            validation_rules (List[IValidationRule]): List abstraksi aturan validasi (Dependency Injection).
        """
        self.validation_rules = validation_rules

    def register_course(self, student: Student, course: Course) -> bool:
        # Mengganti print() dengan LOGGER.info() (Persyaratan 2)
        LOGGER.info(f"\n--- Memulai Pendaftaran {course.code} untuk {student.name} ---")

        for rule in self.validation_rules:
            # Delegasi (SRP): Menyerahkan tugas validasi ke objek Rule
            if not rule.validate(student, course):
                # Mengganti print() dengan LOGGER.info() (Persyaratan 2)
                LOGGER.info(f"⛔ Pendaftaran dibatalkan.")
                return False

        # Jika semua validasi sukses
        student.current_sks += course.sks
        student.schedule.append(course.schedule_code)
        # Mengganti print() dengan LOGGER.info() (Persyaratan 2)
        LOGGER.info(f"✅ Pendaftaran {course.code} berhasil!")
        return True

# ----------------------------------------------------
# 4. Challenge (Pembuktian OCP): Rule Baru
# ----------------------------------------------------

class JadwalBentrokRule(IValidationRule):
    """
    Kelas Konkrit untuk Validasi Bentrokan Jadwal.
    
    Rule baru, ditambahkan tanpa mengubah RegistrationService. Pembuktian OCP.
    """
    def validate(self, student: Student, course: Course) -> bool:
        """Memeriksa apakah jadwal mata kuliah bentrok dengan jadwal mahasiswa."""
        if course.schedule_code in student.schedule:
            # Mengganti print() dengan LOGGER.warning() (Persyaratan 2)
            LOGGER.warning(
                f"❌ GAGAL BENTROK: Jadwal {course.schedule_code} bentrok dengan jadwal "
                f"{student.name} saat ini."
            )
            return False
        return True

# ----------------------------------------------------
# DEMO PROGRAM UTAMA
# ----------------------------------------------------

# Data Uji
student_andi = Student("Andi", current_sks=15, prerequisites_met=True, schedule=['Selasa_10.00', 'Rabu_13.00'])
student_budi = Student("Budi", current_sks=22, prerequisites_met=False, schedule=['Jumat_08.00'])

course_pbo = Course("PBO", sks=3, prerequisite_needed=False, schedule_code='Senin_08.00')
course_pweb = Course("Pweb", sks=4, prerequisite_needed=True, schedule_code='Selasa_10.00') # Bentrok & SKS berlebihan untuk Budi
course_statis = Course("Statis", sks=3, prerequisite_needed=True, schedule_code='Selasa_14.00')


# Skenario 1: Andi (Sukses Murni)
# Setup List Aturan Awal (SKS dan Prasyarat)
initial_rules = [
    SksLimitRule(),
    PrerequisiteRule()
]

# Inject Dependency ke Service
reg_service_andi = RegistrationService(validation_rules=initial_rules)
# print("--- Skenario 1: Andi (Sukses Murni) ---") # Dibiarkan print karena ini output skenario, bukan event sistem
reg_service_andi.register_course(student_andi, course_pbo)

# ----------------------------------------------------
# Pembuktian OCP: Menambahkan Aturan Bentrok (Tanpa Mengubah RegistrationService)
# ----------------------------------------------------

# Skenario 2: Budi (Gagal karena Prasyarat dan SKS)
# Setup List Aturan BARU, termasuk JadwalBentrokRule
ocp_rules = [
    SksLimitRule(),
    PrerequisiteRule(),
    JadwalBentrokRule() # Aturan baru ditambahkan DI SINI
]

# Inject Dependency BARU ke Service
reg_service_budi = RegistrationService(validation_rules=ocp_rules)

print("\n--- Skenario 2: Andi - Gagal Bentrok (Pembuktian OCP) ---") # Dibiarkan print
# Uji Gagal Bentrok (ML memiliki jadwal 'Selasa_10.00' yang sudah dimiliki Andi)
reg_service_budi.register_course(student_andi, course_pweb)

print("\n--- Skenario 3: Budi - Gagal SKS (22 + 4 = 26) ---") # Dibiarkan print
# Uji Gagal SKS (Budi: 22 + 4 = 26 SKS)
reg_service_budi.register_course(student_budi, course_pweb)

print("\n--- Skenario 4: Budi - Gagal Prasyarat ---") # Dibiarkan print
# Uji Gagal Prasyarat (Budi belum memenuhi prasyarat)
reg_service_budi.register_course(student_budi, course_statis)
