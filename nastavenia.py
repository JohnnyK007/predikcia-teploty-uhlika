from PySide6.QtWidgets import QButtonGroup, QCheckBox, QComboBox, QDialog, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QSpinBox, QVBoxLayout, QWidget

# Vytvorenie widgetu s tlačidlami pre opakované použitie
class DialogOknoNastaveni(QDialog):
    def __init__(self):
        super().__init__()
        self.tlacidlo_ulozit = QPushButton('Uložiť')
        self.tlacidlo_zatvorit = QPushButton('Zrušiť')
        dialog_tlac_roz = QHBoxLayout()
        dialog_tlac_roz.addWidget(self.tlacidlo_ulozit)
        dialog_tlac_roz.addWidget(self.tlacidlo_zatvorit)
        self.dialog_tlacidla = QWidget()
        self.dialog_tlacidla.setLayout(dialog_tlac_roz)
        self.tlacidlo_zatvorit.clicked.connect(self.close)


class VseobecneNastavenia(DialogOknoNastaveni):
    def __init__(self, hlavne_okno):
        super().__init__()
        self.setWindowTitle('Všeobecné nastavenia')
        self.hlavne_okno = hlavne_okno
        hlavne_roz = QVBoxLayout()
        oddelovac_roz = QHBoxLayout()
        kodovanie_roz = QHBoxLayout()
        oznacenie_teplota_roz = QHBoxLayout()
        oznacenie_cas_roz = QHBoxLayout()
        oznacenie_uhlik_roz = QHBoxLayout()
        oznacenie_stat_roz = QHBoxLayout()
        oddelovac_oznacenie = QLabel("Oddeľovač dát pre CSV")
        self.oddelovac_lineedit = QLineEdit(self)
        self.oddelovac_lineedit.setFixedSize(20, 26)
        self.oddelovac_lineedit.setText(self.hlavne_okno.oddelovac_dat)
        kodovanie_oznacenie = QLabel("Kódovanie znakov")
        self.kodovanie_dropdown = QComboBox(self)
        self.kodovanie_dropdown.setEditable(True)
        self.kodovanie_dropdown.addItems(["windows-1250", "ascii", "iso-8859-1", "iso-8859-2", "utf-8", "utf-16le", "utf-16be", "windows-1252"])
        self.kodovanie_dropdown.setCurrentText(self.hlavne_okno.kodovanie)

        teplota_oznacenie = QLabel("Označenie teploty")
        self.teplota_lineedit = QLineEdit(self)
        self.teplota_lineedit.setText(self.hlavne_okno.oznacenie_teploty)
        oznacenie_teplota_roz.addWidget(teplota_oznacenie)
        oznacenie_teplota_roz.addWidget(self.teplota_lineedit)

        uhlik_oznacenie = QLabel("Označenie konc. uhlíka")
        self.uhlik_lineedit = QLineEdit(self)
        self.uhlik_lineedit.setText(self.hlavne_okno.oznacenie_uhlika)
        oznacenie_uhlik_roz.addWidget(uhlik_oznacenie)
        oznacenie_uhlik_roz.addWidget(self.uhlik_lineedit)

        cas_oznacenie = QLabel("Označenie časovej osi dyn. dát")
        self.cas_lineedit = QLineEdit(self)
        self.cas_lineedit.setText(self.hlavne_okno.oznacenie_stlpca_dyn)
        oznacenie_cas_roz.addWidget(cas_oznacenie)
        oznacenie_cas_roz.addWidget(self.cas_lineedit)

        stat_oznacenie = QLabel("Označenie x-osi statických dát")
        self.stat_lineedit = QLineEdit(self)
        self.stat_lineedit.setText(self.hlavne_okno.oznacenie_stlpca_stat)
        oznacenie_stat_roz.addWidget(stat_oznacenie)
        oznacenie_stat_roz.addWidget(self.stat_lineedit)

        oznacenia_roz = QVBoxLayout()
        oznacenia_roz.addLayout(oznacenie_stat_roz)
        oznacenia_roz.addLayout(oznacenie_cas_roz)
        oznacenia_roz.addLayout(oznacenie_teplota_roz)
        oznacenia_roz.addLayout(oznacenie_uhlik_roz)
        oznacenia_box = QGroupBox("Označenia stĺpcov v databáze")
        oznacenia_box.setLayout(oznacenia_roz)

        oddelovac_roz.addWidget(oddelovac_oznacenie)
        oddelovac_roz.addWidget(self.oddelovac_lineedit)
        kodovanie_roz.addWidget(kodovanie_oznacenie)
        kodovanie_roz.addWidget(self.kodovanie_dropdown)
        hlavne_roz.addLayout(oddelovac_roz)
        hlavne_roz.addLayout(kodovanie_roz)
        hlavne_roz.addWidget(oznacenia_box)
        self.tlacidlo_ulozit.clicked.connect(self.zmenaVseobecnychNast)
        hlavne_roz.addWidget(self.dialog_tlacidla)
        self.setLayout(hlavne_roz)

    def zmenaVseobecnychNast(self):
        novy_oddelovac_dat = self.oddelovac_lineedit.text()
        self.hlavne_okno.oddelovac_dat = novy_oddelovac_dat
        nove_kodovanie = self.kodovanie_dropdown.currentText()
        self.hlavne_okno.kodovanie = nove_kodovanie
        self.hlavne_okno.oznacenie_teploty = self.teplota_lineedit.text()
        self.hlavne_okno.oznacenie_uhlika = self.uhlik_lineedit.text()
        self.hlavne_okno.oznacenie_stlpca_dyn = self.cas_lineedit.text()
        self.hlavne_okno.oznacenie_stlpca_stat = self.stat_lineedit.text()
        self.close()


class NastaveniaVstupov(DialogOknoNastaveni):
    def __init__(self, hlavne_okno):
        super().__init__()
        self.setWindowTitle('Nastavenia pozorovaní')
        self.hlavne_okno = hlavne_okno
        self.cistyLayout(self.layout())

        hlavne_roz = QVBoxLayout()
        vstupy_roz = QVBoxLayout()
        vstupy_box = QGroupBox("Zvolené pozorovania")
        vstupy_box.setLayout(vstupy_roz)
        self.hlavne_okno.vstupy_checkboxy = []
        zoznam_vstupov = []

        if self.hlavne_okno.stat_poz_nacitane:
            if not self.hlavne_okno.zvolene_vstupy:
                self.hlavne_okno.zvolene_vstupy = self.hlavne_okno.vstupy_stlpce[1:]
            zoznam_vstupov = self.hlavne_okno.vstupy_stlpce[1:]
        elif self.hlavne_okno.ciel_dyn_poz_nacitane:
            zoznam_vstupov = [col for col in self.hlavne_okno.ciele_stlpce[1:] if col not in ["Teplota (°C)", "Uhlík (%)"]]
        for i, vstup in enumerate(zoznam_vstupov):
            vstup_checkbox = QCheckBox(vstup)
            vstup_checkbox.setChecked(vstup in self.hlavne_okno.zvolene_vstupy)
            vstupy_roz.addWidget(vstup_checkbox)
            self.hlavne_okno.vstupy_checkboxy.append(vstup_checkbox)

        hlavne_roz.addWidget(vstupy_box)
        hlavne_roz.addWidget(self.dialog_tlacidla)
        self.tlacidlo_ulozit.clicked.connect(self.zmenaVstupov)
        self.setLayout(hlavne_roz)

    def zmenaVstupov(self):
        nove_vstupy = [checkbox.text() for checkbox in self.hlavne_okno.vstupy_checkboxy if checkbox.isChecked()]
        if nove_vstupy:
            self.hlavne_okno.zvolene_vstupy = nove_vstupy
            if self.hlavne_okno.vstupy_stlpce:
                self.hlavne_okno.vykresliVrchnyGraf()
            if self.hlavne_okno.typ_dat == "dynamické":
                spolocne_stlpce = list(set(self.hlavne_okno.zvolene_vstupy) & set(self.hlavne_okno.ciele_stlpce))
                self.hlavne_okno.zvolene_vstupy = [col for col in spolocne_stlpce if col not in ["Teplota (°C)", "Uhlík (%)"]]
                self.hlavne_okno.vykresliSpodnyGraf()
            self.hlavne_okno.novaSprava("Vybrané pozorovania boli uložené")
            self.close()
        else:
            self.hlavne_okno.novaSprava("Zvoľte aspoň jedno pozorovanie")

    #@staticmethod
    def cistyLayout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    self.cistyLayout(child.layout())


class NastaveniaVystupov(DialogOknoNastaveni):
    def __init__(self, hlavne_okno):
        super().__init__()
        self.setWindowTitle('Nastavenia cieľov')
        self.hlavne_okno = hlavne_okno
        hlavne_roz = QVBoxLayout()
        self.radio_teplota = QRadioButton("Teplota")
        self.radio_uhlik = QRadioButton('Uhlík')
        if self.hlavne_okno.zvoleny_ciel == "Teplota (°C)":
            self.radio_teplota.setChecked(True)
        elif self.hlavne_okno.zvoleny_ciel == "Uhlík (%)":
            self.radio_uhlik.setChecked(True)
        ciele_roz = QVBoxLayout()
        ciele_box = QGroupBox("Zvolený cieľ predikcie (statické dáta)")
        ciele_box.setLayout(ciele_roz)
        ciele_roz.addWidget(self.radio_teplota)
        ciele_roz.addWidget(self.radio_uhlik)
        hlavne_roz.addWidget(ciele_box)
        hlavne_roz.addWidget(self.dialog_tlacidla)
        self.setLayout(hlavne_roz)
        self.tlacidlo_ulozit.clicked.connect(self.zmenaCiela)

    # Zmena vykreslených dát podľa zvoleného výstupu
    def zmenaCiela(self):
        if self.radio_teplota.isChecked():
            novy_ciel = "Teplota (°C)"
        elif self.radio_uhlik.isChecked():
            novy_ciel = "Uhlík (%)"
        else:
            return
        if not self.hlavne_okno.zvoleny_ciel == novy_ciel:
            self.hlavne_okno.zvoleny_ciel = novy_ciel
            if self.hlavne_okno.ciel_dyn_poz_nacitane and self.hlavne_okno.typ_dat=="statické":
                self.hlavne_okno.vykresliSpodnyGraf()
        self.close()


class NastaveniaModelu(DialogOknoNastaveni):
    def __init__(self, hlavne_okno):
        super().__init__()
        self.setWindowTitle('Nastavenia modelu')
        self.hlavne_okno = hlavne_okno
        hlavne_roz = QVBoxLayout()

        # Nastavenia pre statické dáta
        stat_group_box = QGroupBox("Nastavenia pre statické dáta")
        stat_roz = QVBoxLayout()
        pomer_roz = QHBoxLayout()
        pomer_dat = QLabel("Pomer trénovacích dát")
        self.pomer_dat_spinbox = QSpinBox()
        self.pomer_dat_spinbox.setFixedSize(85, 26)
        self.pomer_dat_spinbox.setRange(0, 100)
        self.pomer_dat_spinbox.setSingleStep(1)
        self.pomer_dat_spinbox.setValue(self.hlavne_okno.pomer_dat)
        pomer_roz.addWidget(pomer_dat)
        pomer_roz.addWidget(self.pomer_dat_spinbox)
        stat_roz.addLayout(pomer_roz)
        stat_group_box.setLayout(stat_roz)

        # Výber modelu
        model_group_box = QGroupBox("Model")
        model_roz = QVBoxLayout()
        self.radio_SVR = QRadioButton("Support Vector Regression")
        self.radio_RF = QRadioButton("Random Forest")
        self.radio_NN = QRadioButton("Neural Network")
        self.radio_model_group = QButtonGroup()
        self.radio_model_group.addButton(self.radio_SVR)
        self.radio_model_group.addButton(self.radio_RF)
        self.radio_model_group.addButton(self.radio_NN)
        model_roz.addWidget(self.radio_SVR)
        model_roz.addWidget(self.radio_RF)
        model_roz.addWidget(self.radio_NN)
        model_group_box.setLayout(model_roz)

        # Jadrová funkcia SVR
        self.kernel_group_box = QGroupBox("Jadrová funkcia pre model SVR")
        kernel_roz = QVBoxLayout()
        self.radio_SVRGauss = QRadioButton("Gaussova regresia")
        self.radio_SVRpolynom = QRadioButton("Polynomická regresia")
        self.radio_kernel_group = QButtonGroup()
        self.radio_kernel_group.addButton(self.radio_SVRGauss)
        self.radio_kernel_group.addButton(self.radio_SVRpolynom)
        kernel_roz.addWidget(self.radio_SVRGauss)
        kernel_roz.addWidget(self.radio_SVRpolynom)
        self.kernel_group_box.setLayout(kernel_roz)

        # Nastavenia pre neurónové siete
        self.NN_group_box = QGroupBox("Nastavenia modelu neurónových sietí")
        NN_roz = QVBoxLayout()
        NN_neurony_roz = QHBoxLayout()
        NN_neurony = QLabel("Počet neurónov skrytých vrstiev (napr. 32, 16)")
        self.NN_neurony_lineedit = QLineEdit()
        self.NN_neurony_lineedit.setFixedSize(85, 26)
        if self.hlavne_okno.pocet_NN_vrstiev:
            self.NN_neurony_lineedit.setText(", ".join(map(str, self.hlavne_okno.pocet_NN_vrstiev)))
        else:
            self.NN_neurony_lineedit.setText("auto")
        NN_neurony_roz.addWidget(NN_neurony)
        NN_neurony_roz.addWidget(self.NN_neurony_lineedit)
        NN_roz.addLayout(NN_neurony_roz)
        self.NN_group_box.setLayout(NN_roz)

        hlavne_roz.addWidget(stat_group_box)
        hlavne_roz.addWidget(model_group_box)
        hlavne_roz.addWidget(self.kernel_group_box)
        hlavne_roz.addWidget(self.NN_group_box)
        hlavne_roz.addWidget(self.dialog_tlacidla)
        self.setLayout(hlavne_roz)
        self.zobrazenieKernelu()
        self.zobrazenieNNnastaveni()
        self.radio_SVR.toggled.connect(self.zobrazenieKernelu)
        self.radio_NN.toggled.connect(self.zobrazenieNNnastaveni)
        if self.hlavne_okno.zvoleny_model == "SVR":
            self.radio_SVR.setChecked(True)
        elif self.hlavne_okno.zvoleny_model == "RF":
            self.radio_RF.setChecked(True)
        elif self.hlavne_okno.zvoleny_model == "NN":
            self.radio_NN.setChecked(True)
        if self.hlavne_okno.zvoleny_kernel == "rbf":
            self.radio_SVRGauss.setChecked(True)
        elif self.hlavne_okno.zvoleny_kernel == "poly":
            self.radio_SVRpolynom.setChecked(True)
        self.tlacidlo_ulozit.clicked.connect(self.zmenaPomeruDat)
        self.tlacidlo_ulozit.clicked.connect(self.zmenaModelu)
        self.tlacidlo_ulozit.clicked.connect(self.zmenaKernelu)
        self.tlacidlo_ulozit.clicked.connect(self.zmenaNN)
        self.tlacidlo_ulozit.clicked.connect(self.close)

    def zmenaPomeruDat(self):
        self.hlavne_okno.pomer_dat = self.pomer_dat_spinbox.value()

    def zmenaModelu(self):
        if self.radio_SVR.isChecked():
            self.hlavne_okno.zvoleny_model = "SVR"
        elif self.radio_RF.isChecked():
            self.hlavne_okno.zvoleny_model = "RF"
        elif self.radio_NN.isChecked():
            self.hlavne_okno.zvoleny_model = "NN"

    def zmenaKernelu(self):
        if self.radio_SVRGauss.isChecked():
            self.hlavne_okno.zvoleny_kernel = "rbf"
        elif self.radio_SVRpolynom.isChecked():
            self.hlavne_okno.zvoleny_kernel = "poly"

    def zobrazenieKernelu(self):
        if self.radio_SVR.isChecked():
            self.kernel_group_box.show()
        else:
            self.kernel_group_box.hide()

    def zmenaNN(self):
        pocet_NN_vrstiev_text = self.NN_neurony_lineedit.text().strip()
        try:
            NN_hodnoty = [int(x.strip()) for x in pocet_NN_vrstiev_text.split(',') if x.strip()]
            if NN_hodnoty:
                self.hlavne_okno.pocet_NN_vrstiev = tuple(NN_hodnoty)
        except ValueError:
            self.hlavne_okno.novaSprava("Nebol zadaný platný vstup pre konfiguráciu skrytých NN vrstiev. Použije sa automatická konfigurácia.")

    def zobrazenieNNnastaveni(self):
        if self.radio_NN.isChecked():
            self.NN_group_box.show()
        else:
            self.NN_group_box.hide()


class DynTepUhlik(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Meraná teplota a uhlík v zač. a konc. bode")
        self.setMinimumWidth(300)
        self.vysledky: dict[str, float | None] = {"teplota_zac": None,"teplota_konc": None,"uhlik_zac": None,"uhlik_konc": None}
        layout = QVBoxLayout()
        self.teplota_zac = QLineEdit()
        self.teplota_konc = QLineEdit()
        self.uhlik_zac = QLineEdit()
        self.uhlik_konc = QLineEdit()

        def pridaj_riadok(popis, lineedit):
            riadok = QHBoxLayout()
            label = QLabel(popis)
            label.setFixedWidth(180)
            riadok.addWidget(label)
            lineedit.setFixedWidth(80)
            riadok.addWidget(lineedit)
            return riadok
        layout.addLayout(pridaj_riadok("Začiatočná teplota (°C):", self.teplota_zac))
        layout.addLayout(pridaj_riadok("Koncová teplota (°C):", self.teplota_konc))
        layout.addLayout(pridaj_riadok("Začiatočná koncentrácia uhlíka (%):", self.uhlik_zac))
        layout.addLayout(pridaj_riadok("Koncová koncentrácia uhlíka (%):", self.uhlik_konc))
        poznamka = QLabel('Ak hodnoty nepoznáte, len stlačte tlačidlo "Potvrdiť".')
        poznamka.setStyleSheet("font-style: italic; color: gray;")
        layout.addWidget(poznamka)
        tlac_ulozit = QPushButton("Potvrdiť")
        tlac_ulozit.clicked.connect(self.ulozMerane)
        layout.addWidget(tlac_ulozit)
        self.setLayout(layout)

    def ulozMerane(self):
        def nacitajHodnotu(edit):
            text = edit.text().strip().replace(",", ".")
            try:
                return float(text) if text else None
            except ValueError:
                return None
        self.vysledky["teplota_zac"] = nacitajHodnotu(self.teplota_zac)
        self.vysledky["teplota_konc"] = nacitajHodnotu(self.teplota_konc)
        self.vysledky["uhlik_zac"] = nacitajHodnotu(self.uhlik_zac)
        self.vysledky["uhlik_konc"] = nacitajHodnotu(self.uhlik_konc)
        self.accept()