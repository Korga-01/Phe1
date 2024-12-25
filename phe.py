import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from openfhe import *

# Настройка контекста OpenFHE
params = CryptoParamsCKKSRNS()
params.SetMultiplicativeDepth(5)
params.SetScalingModSize(50)
params.SetScalingTechnique(ScalingTechnique.FLEXIBLEAUTO)
params.SetBatchSize(8)

cc = GenCryptoContext(params)
cc.Enable(PKESchemeFeature.PKE)
cc.Enable(PKESchemeFeature.KEYSWITCH)
cc.Enable(PKESchemeFeature.LEVELEDSHE)

keys = cc.KeyGen()
cc.EvalMultKeyGen(keys.secretKey)

# Пример таблицы клиентов
data = {
    "ID": [1, 2, 3],
    "Name": ["Иван Иванов", "Петр Петров", "Светлана Сидорова"],
    "Account Balance": [1000.0, 2000.0, 1500.0],
    "Last Operation": ["Депозит 1000", "Снятие 500", "Депозит 1500"]
}

df = pd.DataFrame(data)

# Функция для шифрования
def encrypt_data():
    encrypted_data = []
    for index, row in df.iterrows():
        balance = row["Account Balance"]
        plaintext = cc.MakeCKKSPackedPlaintext([balance])
        ciphertext = cc.Encrypt(keys.publicKey, plaintext)
        encrypted_data.append(ciphertext)
    return encrypted_data

# Функция для дешифрования
def decrypt_data(encrypted_data):
    decrypted_data = []
    for ciphertext in encrypted_data:
        decrypted_plaintext = cc.Decrypt(keys.secretKey, ciphertext)
        decrypted_value = decrypted_plaintext.GetRealPackedValue()[0]
        decrypted_data.append(decrypted_value)
    return decrypted_data

# Редактирование зашифрованных данных
def update_encrypted_data():
    encrypted_data = encrypt_data()
    decrypted_data = decrypt_data(encrypted_data)
    
    # Обновляем значения в таблице
    for i, val in enumerate(decrypted_data):
        df.at[i, "Account Balance"] = val
    update_table()

# Обновление таблицы в интерфейсе
def update_table():
    for row in range(table.rowCount()):
        for col in range(table.columnCount()):
            item = table.item(row, col)
            item.setText(str(df.iloc[row, col]))

# Основное окно приложения
class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bank Client Data Encryption")
        self.setGeometry(100, 100, 800, 400)

        # Таблица
        self.table = QTableWidget(self)
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns)

        for i, row in df.iterrows():
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

        # Кнопки для шифрования и дешифрования
        encrypt_button = QPushButton("Шифровать данные", self)
        encrypt_button.clicked.connect(lambda: encrypt_data())

        decrypt_button = QPushButton("Дешифровать данные", self)
        decrypt_button.clicked.connect(lambda: update_encrypted_data())

        update_button = QPushButton("Обновить зашифрованные данные", self)
        update_button.clicked.connect(update_encrypted_data)

        # Размещение виджетов
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        button_layout.addWidget(encrypt_button)
        button_layout.addWidget(decrypt_button)
        button_layout.addWidget(update_button)

        layout.addWidget(self.table)
        layout.addLayout(button_layout)

        self.setLayout(layout)

# Запуск приложения
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
