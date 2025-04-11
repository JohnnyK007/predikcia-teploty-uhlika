# Inštalácia knižníc pomocou "pip install nazov_kniznice"
#    pip install python-calamine (pre prácu s Excel a OpenDocument súbormi)
# Importovanie knižníc
import os
import webbrowser
import pandas
import seaborn
import numpy

#from pip._vendor.rich.align import Align
from sklearn.base import clone
from sklearn.metrics import mean_squared_error
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from PySide6.QtWidgets import QApplication, QButtonGroup, QCheckBox, QComboBox, QDialog, QErrorMessage, QFileDialog, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QRadioButton, QScrollArea, QSpinBox, QSplitter, QTextEdit, QVBoxLayout, QWidget
from PySide6.QtGui import QAction, QPalette
from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
# noinspection PyPep8Naming

class DialogOknoNastaveni(QDialog):
    def __init__(self):
        super().__init__()

        # Vytvorenie widgetu s tlačidlami pre opakované použitie
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
        oddelovac_oznacenie = QLabel("Oddeľovač dát pre CSV")
        self.oddelovac_lineedit = QLineEdit(self)
        self.oddelovac_lineedit.setFixedSize(20, 26)
        self.oddelovac_lineedit.setText(self.hlavne_okno.oddelovac_dat)
        kodovanie_oznacenie = QLabel("Kódovanie znakov")
        self.kodovanie_dropdown = QComboBox(self)
        self.kodovanie_dropdown.setEditable(True)
        self.kodovanie_dropdown.addItems(["windows-1250", "ascii", "iso-8859-1", "iso-8859-2", "utf-8", "utf-16le", "utf-16be", "windows-1252"])
        self.kodovanie_dropdown.setCurrentText(self.hlavne_okno.kodovanie)
        hlavne_roz.addLayout(oddelovac_roz)
        hlavne_roz.addLayout(kodovanie_roz)
        oddelovac_roz.addWidget(oddelovac_oznacenie)
        oddelovac_roz.addWidget(self.oddelovac_lineedit)
        kodovanie_roz.addWidget(kodovanie_oznacenie)
        kodovanie_roz.addWidget(self.kodovanie_dropdown)
        self.tlacidlo_ulozit.clicked.connect(self.zmenaVseobecnychNast)
        hlavne_roz.addWidget(self.dialog_tlacidla)
        self.setLayout(hlavne_roz)

    def zmenaVseobecnychNast(self):
        novy_oddelovac_dat = self.oddelovac_lineedit.text()
        self.hlavne_okno.oddelovac_dat = novy_oddelovac_dat
        nove_kodovanie = self.kodovanie_dropdown.currentText()
        self.hlavne_okno.kodovanie = nove_kodovanie
        self.close()


class NastaveniaVstupov(DialogOknoNastaveni):
    def __init__(self, hlavne_okno):
        super().__init__()
        self.setWindowTitle('Nastavenia vstupov')
        self.hlavne_okno = hlavne_okno
        self.cistyLayout(self.layout())

        hlavne_roz = QVBoxLayout()
        vstupy_roz = QVBoxLayout()
        vstupy_box = QGroupBox("Povolené vstupy")
        vstupy_box.setLayout(vstupy_roz)
        self.hlavne_okno.vstupy_checkboxy = []

        if self.hlavne_okno.vstupy_stlpce:
            if not self.hlavne_okno.zvolene_vstupy:
                self.hlavne_okno.zvolene_vstupy = self.hlavne_okno.vstupy_stlpce[1:]
            for i, vstup in enumerate(self.hlavne_okno.vstupy_stlpce[1:]):
                vstup_checkbox = QCheckBox(vstup)
                vstup_checkbox.setChecked(vstup in self.hlavne_okno.zvolene_vstupy)
                vstupy_roz.addWidget(vstup_checkbox)
                self.hlavne_okno.vstupy_checkboxy.append(vstup_checkbox)

        hlavne_roz.addWidget(vstupy_box)
        hlavne_roz.addWidget(self.dialog_tlacidla)
        self.tlacidlo_ulozit.clicked.connect(self.zmenaVstupov)
        self.setLayout(hlavne_roz)

    def zmenaVstupov(self):
        if self.hlavne_okno.vstupy_stlpce:
            nove_vstupy = [checkbox.text() for checkbox in self.hlavne_okno.vstupy_checkboxy if checkbox.isChecked()]
            if nove_vstupy:
                self.hlavne_okno.zvolene_vstupy = nove_vstupy
                self.hlavne_okno.vykreslenieDat("vstupy")
                self.hlavne_okno.novaSprava("Vybrané vstupy boli uložené")
                self.close()
            else:
                self.hlavne_okno.novaSprava("Zvoľte aspoň jeden vstup")

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
        self.setWindowTitle('Nastavenia výstupov')
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

    def zmenaCiela(self):
        if self.radio_teplota.isChecked():
            novy_ciel = "Teplota (°C)"
        elif self.radio_uhlik.isChecked():
            novy_ciel = "Uhlík (%)"
        else:
            return

        # Zmena vykreslených dát podľa zvoleného výstupu
        if not self.hlavne_okno.zvoleny_ciel == novy_ciel:
            self.hlavne_okno.zvoleny_ciel = novy_ciel
            if self.hlavne_okno.data_nacitane and self.hlavne_okno.typ_dat=="statické":
                self.hlavne_okno.vykreslenieDat("ciele")

        self.close()


class NastaveniaModelu(DialogOknoNastaveni):
    def __init__(self, hlavne_okno):
        super().__init__()
        self.setWindowTitle('Nastavenia modelu')
        self.hlavne_okno = hlavne_okno
        hlavne_roz = QVBoxLayout()

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

        # Vytvorenie skupiny pre výber modelu
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

        # Vytvorenie skupiny pre výber jadrovej funkcie
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

        # Vytvorenie skupiny pre nastavenia NN
        self.NN_group_box = QGroupBox("Nastavenia modelu neurónových sietí")
        NN_roz = QVBoxLayout()
        NN_neurony_roz = QHBoxLayout()
        NN_neurony = QLabel("Počet neurónov")
        self.NN_neurony_lineedit = QLineEdit()
        self.NN_neurony_lineedit.setFixedSize(85, 26)
        self.NN_neurony_lineedit.setText(", ".join(map(str, self.hlavne_okno.pocet_NN_vrstiev)))
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

        if self.hlavne_okno.zvoleny_kernel == "Gaussova regresia":
            self.radio_SVRGauss.setChecked(True)
        elif self.hlavne_okno.zvoleny_kernel == "polynomická regresia":
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
            self.hlavne_okno.zvoleny_kernel = "Gaussova regresia"
        elif self.radio_SVRpolynom.isChecked():
            self.hlavne_okno.zvoleny_kernel = "polynomická regresia"

    def zobrazenieKernelu(self):
        if self.radio_SVR.isChecked():
            self.kernel_group_box.show()
        else:
            self.kernel_group_box.hide()

    def zmenaNN(self):
        pocet_NN_vrstiev_text = self.NN_neurony_lineedit.text()
        self.hlavne_okno.pocet_NN_vrstiev = tuple(int(x.strip()) for x in pocet_NN_vrstiev_text.split(','))

    def zobrazenieNNnastaveni(self):
        if self.radio_NN.isChecked():
            self.NN_group_box.show()
        else:
            self.NN_group_box.hide()


class HlavneOkno(QMainWindow):

    def __init__(self):
        super().__init__()
        #self.overlay()

        # Deklarácia globálnych premenných
        self.data_vstupy = pandas.DataFrame()
        self.data_ciele = pandas.DataFrame()
        #self.matica_vstupov = pandas.DataFrame()
        #self.matica_ciela_tren = pandas.DataFrame()
        self.matica_ciela_test = pandas.DataFrame()
        self.nazov_databazy = str
        self.chybove_okno = QErrorMessage(self)
        self.chybove_okno.setWindowTitle("Chyba")
        self.kodovanie = "windows-1250"
        self.oddelovac_dat = ";"
        self.pomer_dat = 70
        self.zvoleny_model = "SVR"
        self.zvoleny_kernel = "polynomická regresia"
        self.zvoleny_ciel = "Teplota (°C)"
        self.zvolene_vstupy = list
        self.vstupy_stlpce = list
        self.vstupy_checkboxy = list
        self.model = None
        self.data_nacitane = False
        self.pocet_NN_vrstiev = (32, 16)
        self.oznacenie_stlpca_stat = "Tavba č."
        self.oznacenie_stlpca_dyn = "Čas (s)"
        self.typ_dat = str
        self.os_x = str
        self.predikcia_teplota = None
        self.predikcia_uhlik = None
        self.farba_popredia = "black"
        self.farba_pozadia = "white"
        self.data_zvol_vstupy = pandas.DataFrame()

    #def overlay(self):
        # Nastavenia hlavného okna
        self.setWindowTitle("Predikcia a modelovanie")
        self.setGeometry(120, 80, 1300, 700)
        self.showMaximized()

        # Vytvorenie menu a položiek menu
        navbar = self.menuBar()
        menu_subor = navbar.addMenu("Dáta")
        polozka_predikcia = QAction("Predikcia", self)
        polozka_predikcia.triggered.connect(self.volbaModelu)
        navbar.addAction(polozka_predikcia)
        menu_nastavenia = navbar.addMenu("Nastavenia")
        menu_pomoc = navbar.addMenu("Info")

        # Vytvorenie podmenu Dáta a jeho položiek
        polozka_nacitat_vstupy = QAction("Načítať vstupy", self)
        polozka_nacitat_vstupy.triggered.connect(lambda: self.otvorit("vstupy"))
        menu_subor.addAction(polozka_nacitat_vstupy)
        polozka_nacitat_ciele = QAction("Načítať ciele predikcie", self)
        polozka_nacitat_ciele.triggered.connect(lambda: self.otvorit("ciele"))
        menu_subor.addAction(polozka_nacitat_ciele)
        polozka_export = QAction("Exportovať výsledky", self)
        polozka_export.triggered.connect(self.exportPredikcie)
        menu_subor.addAction(polozka_export)

        # Vytvorenie podmenu Nastavenia a jeho položiek
        polozka_nast_vseobecne = QAction("Všeobecné", self)
        polozka_nast_vseobecne.triggered.connect(self.vseobecneNastavenia)
        menu_nastavenia.addAction(polozka_nast_vseobecne)
        polozka_nast_vstupov = QAction("Vstupy", self)
        polozka_nast_vstupov.triggered.connect(self.nastaveniaVstupov)
        menu_nastavenia.addAction(polozka_nast_vstupov)
        polozka_nast_vystupov = QAction("Výstupy", self)
        polozka_nast_vystupov.triggered.connect(self.nastaveniaVystupov)
        menu_nastavenia.addAction(polozka_nast_vystupov)
        polozka_nast_modelu = QAction("Model", self)
        polozka_nast_modelu.triggered.connect(self.nastaveniaModelu)
        menu_nastavenia.addAction(polozka_nast_modelu)

        # Vytvorenie podmenu Info a jeho položiek
        polozka_pomocnik = QAction("Pomocník", self)
        polozka_pomocnik.triggered.connect(self.pomocnik)
        menu_pomoc.addAction(polozka_pomocnik)
        polozka_o = QAction("O aplikácii", self)
        polozka_o.triggered.connect(self.o)
        menu_pomoc.addAction(polozka_o)

        # Vytvorenie textového okna pre konzolu
        self.vystup_textu = QTextEdit()
        self.vystup_textu.setReadOnly(True)

        # Vytvorenie skrolovacej oblasti pre konzolu (spodný widget)
        skrol_area = QScrollArea()
        skrol_area.setWidgetResizable(True)
        skrol_area.setWidget(self.vystup_textu)
        konzola_roz = QVBoxLayout()
        konzola_roz.addWidget(skrol_area)
        konzola = QGroupBox()
        konzola.setTitle("Konzola")
        konzola.setLayout(konzola_roz)

        # Rozvrhnutie grafov ----------------------------
        grafy = FigureCanvas(Figure(figsize=(5, 3)))
        grafy_roz = QVBoxLayout()
        grafy_roz.addWidget(NavigationToolbar(grafy, self))
        grafy_roz.addWidget(grafy)
        graf_zobrazenie = QGroupBox()
        graf_zobrazenie.setTitle("Grafy")
        graf_zobrazenie.setLayout(grafy_roz)

        # Grafy
        self.graf_pozorovania, self.graf_ciele = grafy.figure.subplots(2, 1)
        self.resetGrafov()

        # Rozdeľovač
        rozdelovac = QSplitter(Qt.Vertical)
        rozdelovac.addWidget(graf_zobrazenie)
        rozdelovac.addWidget(konzola)
        rozdelovac.setSizes([850, 150])

        # Hlavné vertikálne rozvrhnutie widgetov
        rozlozenie = QVBoxLayout()
        rozlozenie.addWidget(rozdelovac)

        # Vytvorenie hlavného rámu aplikácie
        hlavny_frame = QWidget()
        hlavny_frame.setLayout(rozlozenie)
        self.setCentralWidget(hlavny_frame)

    def novaSprava(self, sprava):
        self.vystup_textu.append(sprava)

    def resetGrafov(self):
        self.graf_pozorovania.cla()
        self.graf_ciele.cla()
        self.graf_pozorovania.grid(True)
        self.graf_ciele.grid(True)
        self.tmavyRezim(self)
        self.graf_pozorovania.figure.canvas.draw_idle()
        self.graf_ciele.figure.canvas.draw_idle()

    def otvorit(self, dataframeIO):
        predvoleny_priecinok = os.path.abspath(os.getcwd())
        self.nazov_databazy, filtr = QFileDialog.getOpenFileName(None, "Otvoriť súbor", predvoleny_priecinok, "CSV súbory (*.csv);;Súbory programu Microsoft Excel (*.xlsx *.xls *.xlsb *.xlsm);;Súbory typu OpenDocument (*.ods);;Textové súbory (*.txt);;Všetky súbory (*.*)")
        if self.nazov_databazy:
            try:
                _, pripona_suboru = os.path.splitext(self.nazov_databazy)
                pripona_suboru = pripona_suboru.lower()
                if pripona_suboru in [".csv", ".txt"]:
                    dataframe = pandas.read_csv(self.nazov_databazy, delimiter=self.oddelovac_dat, encoding=self.kodovanie, header=0)
                elif pripona_suboru in [".xlsx", ".xls", ".ods", ".xlsb", ".xlsm"]:
                    dataframe = pandas.read_excel(self.nazov_databazy, engine="calamine")
                else:
                    raise ValueError("Nepodporovaný formát súboru")
                self.novaSprava(f"Súbor {self.nazov_databazy} bol úspešne otvorený")
                self.zvolene_vstupy = []
                pocet_stlpcov = None
                pocet_riadkov = None

                if dataframeIO == "vstupy":
                    self.data_vstupy = dataframe
                    pocet_riadkov, pocet_stlpcov = self.data_vstupy.shape
                    pocet_riadkov -= 1

                elif dataframeIO == "ciele":
                    self.data_ciele = dataframe
                    pocet_riadkov, pocet_stlpcov = self.data_ciele.shape
                    pocet_riadkov -= 1

                sprava_data = ""

                if pocet_stlpcov == 1:
                    sprava_data = f"Načítaný {pocet_stlpcov} stĺpec"
                elif 2 <= pocet_stlpcov <= 4:
                    sprava_data = f"Načítané {pocet_stlpcov} stĺpce"
                elif pocet_stlpcov > 4:
                    sprava_data = f"Načítaných {pocet_stlpcov} stĺpcov"

                if pocet_riadkov == 1:
                    sprava_data += f" a {pocet_riadkov} riadok dát"
                elif 2 <= pocet_riadkov <= 4:
                    sprava_data += f" a {pocet_riadkov} riadky dát"
                elif pocet_riadkov > 4:
                    sprava_data += f" a {pocet_riadkov} riadkov dát"
                self.novaSprava(sprava_data)
                self.data_nacitane = True

            except ValueError as chyba:
                self.chybove_okno.showMessage(f"Neočakávané hodnoty:<br>{str(chyba)}")
                self.novaSprava(f"Neočakávané hodnoty v súbore {self.nazov_databazy}")
            except (UnicodeDecodeError, pandas.errors.ParserError) as chyba:
                self.chybove_okno.showMessage(f"Chyba pri spracovaní súboru:<br>{str(chyba)}")
                self.novaSprava(f"Chyba pri dekódovaní súboru {self.nazov_databazy}")
            except Exception as chyba:
                self.chybove_okno.showMessage(f"Neočakávaná chyba:<br>{str(chyba)}")
                self.novaSprava(f"Neočakávaná chyba pri otváraní súboru {self.nazov_databazy}")

            finally:
                self.vykreslenieDat(dataframeIO)

    def vykreslenieDat(self, dataframeIO):
        if dataframeIO == "vstupy":
            self.graf_pozorovania.cla()
            self.tmavyRezim(self)
            self.graf_pozorovania.set_title('Pozorovania', color=self.farba_popredia)
            self.graf_pozorovania.grid(True)
            self.vstupy_stlpce = self.data_vstupy.columns[:].tolist()

            if self.oznacenie_stlpca_stat in self.vstupy_stlpce:
                self.os_x = self.oznacenie_stlpca_stat
            elif self.oznacenie_stlpca_dyn in self.vstupy_stlpce:
                self.os_x = self.oznacenie_stlpca_dyn
            else:
                self.data_vstupy.reset_index(inplace=True)
                self.os_x = "index"

            vykreslene_vstupy = self.zvolene_vstupy if self.zvolene_vstupy else self.vstupy_stlpce[1:]
            if self.os_x not in vykreslene_vstupy:
                vykreslene_vstupy = [self.os_x] + vykreslene_vstupy
            self.data_zvol_vstupy = self.data_vstupy[vykreslene_vstupy].copy()
            nac_data_vstupy = self.data_zvol_vstupy.melt(id_vars=self.os_x, var_name="Názov stĺpca", value_name="")
            plot1 = seaborn.lineplot(data=nac_data_vstupy, x=self.os_x, y="", hue="Názov stĺpca", ax=self.graf_pozorovania)
            plot1.legend(loc="upper left", bbox_to_anchor=(1.01, 1.1))
            plot1.set_xlabel(self.os_x, labelpad=-10, x=-0.03, color=self.farba_popredia)
            xlim_max = self.data_vstupy.index.max()
            plot1.set_xlim(0, xlim_max)
            self.graf_pozorovania.figure.canvas.draw_idle()
            if "index" in self.data_vstupy.columns:
                self.data_vstupy.drop(columns=["index"], inplace=True)

        elif dataframeIO == "ciele":
            self.graf_ciele.cla()
            self.tmavyRezim(self)
            self.graf_ciele.set_title('Ciele predikcie', color=self.farba_popredia)
            self.graf_ciele.grid(True)
            ciele_stlpce = self.data_ciele.columns[:].tolist()
            nac_data_ciele = pandas.DataFrame()
            plot2 = seaborn.lineplot()
            if self.oznacenie_stlpca_stat in ciele_stlpce:
                self.typ_dat = "statické"
                self.novaSprava("Zistené statické dáta")
                self.os_x = self.oznacenie_stlpca_stat
                if self.zvoleny_ciel == "Teplota (°C)":
                    nac_data_ciele = self.data_ciele.melt(id_vars=self.os_x, value_vars="Teplota (°C)", var_name="Teplota", value_name="(°C)")
                    plot2 = seaborn.lineplot(data=nac_data_ciele, x=self.os_x, y="(°C)", hue="Teplota", ax=self.graf_ciele, color="blue")
                elif self.zvoleny_ciel == "Uhlík (%)":
                    nac_data_ciele = self.data_ciele.melt(id_vars=self.os_x, value_vars="Uhlík (%)", var_name="Koncentrácia uhlíka", value_name="(%)")
                    plot2 = seaborn.lineplot(data=nac_data_ciele, x=self.os_x, y="(%)", hue="Koncentrácia uhlíka", ax=self.graf_ciele, color="blue")
                plot2.legend(loc="lower left", bbox_to_anchor=(0, -0.30), ncol=10)

            elif self.oznacenie_stlpca_dyn in ciele_stlpce:
                self.typ_dat = "dynamické"
                self.novaSprava("Zistené dynamické dáta")
                self.os_x = self.oznacenie_stlpca_dyn
                nac_data_ciele = self.data_ciele.melt(id_vars=self.os_x, var_name="Názov stĺpca", value_name="")
                plot2 = seaborn.lineplot(data=nac_data_ciele, x=self.os_x, y="", hue="Názov stĺpca", ax=self.graf_ciele, color="blue")
                plot2.legend(loc="lower left", bbox_to_anchor=(-0.05, -0.30), ncol=11)

            else:
                self.novaSprava("Nezistený typ dát")
                self.chybove_okno.showMessage("Nezistený typ dát.<br>Nie je možné rozpoznať stĺpec s časom alebo por. číslami tavieb.")
            plot2.set_xlabel(self.os_x, labelpad=-10, x=-0.03, color=self.farba_popredia)
            xlim_max = nac_data_ciele[self.os_x].max()
            plot2.set_xlim(0, xlim_max)
            self.graf_ciele.figure.canvas.draw_idle()

    def exportPredikcie(self):
        dataframe_predikcia = pandas.DataFrame()
        print(f"zvoleny_ciel:\n{self.zvoleny_ciel}predikcia_uhlik:\n{self.predikcia_uhlik}\npredikcia_teplota:\n{self.predikcia_teplota}\nmerany_ciel:\n{self.merany_ciel}")
        if self.predikcia_uhlik is not None or self.predikcia_teplota is not None:
            file_path, _ = QFileDialog.getSaveFileName(None, "Exportovať dáta", "", "CSV súbory (*.csv);;Všetky súbory (*)")

            if file_path:
                data = {}

                if self.typ_dat == "statické":
                    if self.zvoleny_ciel == "Teplota (°C)":
                        data["Meraná teplota (°C)"] = self.merany_ciel
                    if self.zvoleny_ciel == "Uhlík (%)":
                        data["Meraný uhlík (%)"] = self.merany_ciel

                if self.predikcia_teplota is not None and len(self.predikcia_teplota) > 0:
                    data["Predikovaná teplota (°C)"] = self.predikcia_teplota

                if self.predikcia_uhlik is not None and len(self.predikcia_uhlik) > 0:
                    data["Predikovaný uhlík (°C)"] = self.predikcia_uhlik
                print(f"data:\n{data}\ndataframe_predikcia:\n{dataframe_predikcia}")
                if data: dataframe_predikcia = pandas.DataFrame(data)

                # Uloženie do CSV
                dataframe_predikcia.to_csv(file_path, index=False, sep=self.oddelovac_dat, encoding=self.kodovanie)
                self.novaSprava(f"Výsledky predikcie s využitím modelu {self.zvoleny_model} boli uložené do priečinku {file_path}")
                if self.typ_dat == "statické": self.novaSprava("-Trénovacia a testovacia časť statických dát je oddelená prázdnym riadkom-")

        else:
            self.novaSprava("Žiadne dáta na export. Najprv vykonajte predikciu.")

    def vseobecneNastavenia(self):
        okno_nast_vseobecne = VseobecneNastavenia(hlavne_okno=self)
        okno_nast_vseobecne.exec()
        self.novaSprava(f'Oddeľovač hodnôt CSV databázy bol nastavený na "{self.oddelovac_dat}" a kódovanie znakov na "{self.kodovanie}"')

    def nastaveniaVstupov(self):
        okno_nast_vstupov = NastaveniaVstupov(hlavne_okno=self)
        okno_nast_vstupov.exec()

    def nastaveniaVystupov(self):
        okno_nast_vystupov = NastaveniaVystupov(hlavne_okno=self)
        okno_nast_vystupov.exec()
        if self.zvoleny_ciel == "Teplota (°C)":
            self.novaSprava("Teplota (°C) bola nastavená ako cieľ predikcie")
        elif self.zvoleny_ciel == "Uhlík (%)":
            self.novaSprava("Uhlík (%) bol nastavený ako cieľ predikcie")

    def nastaveniaModelu(self):
        okno_nast_modelu = NastaveniaModelu(hlavne_okno=self)
        okno_nast_modelu.exec()
        if self.zvoleny_model == "SVR":
            self.novaSprava("Model predikcie bol nastavený na " + self.zvoleny_model + " a jeho jadrová funkcia na typ " + self.zvoleny_kernel)
        elif self.zvoleny_model == "NN":
            self.novaSprava("Model predikcie bol nastavený na " + self.zvoleny_model + " a počet neurónov pre jednotlivé skryté vrstvy na " + str(self.pocet_NN_vrstiev))
        else:
            self.novaSprava("Model predikcie bol nastavený na " + self.zvoleny_model)
        self.novaSprava("Pomer trénovacích dát bol nastavený na " + str(self.pomer_dat) + "%")

    def volbaModelu(self):
        if not self.data_vstupy.empty and not self.data_ciele.empty:
            if self.zvoleny_model == "SVR":
                if self.zvoleny_kernel == "Gaussova regresia":
                    self.model = SVR(kernel='rbf', C=20, epsilon=0.001)
                elif self.zvoleny_kernel == "polynomická regresia":
                    self.model = SVR(kernel='poly', C=10, degree=2, coef0=10)
            elif self.zvoleny_model == "RF":
                self.model = RandomForestRegressor(random_state=17, n_jobs=-1)
            elif self.zvoleny_model == "NN":
                self.model = MLPRegressor(hidden_layer_sizes=self.pocet_NN_vrstiev, solver="lbfgs", learning_rate="adaptive", alpha=0.0001, max_iter=200, random_state=17)
                # parametre = {
                #     'hidden_layer_sizes': [(64,), (16, 16), (32, 16)],
                #     'alpha': [0.0001, 0.001, 0.01],
                #     'solver': ['lbfgs'],
                #     'learning_rate': ['adaptive', 'constant'],
                #     'learning_rate_init': [0.001, 0.01],
                # }
                # self.model = GridSearchCV(MLPRegressor(max_iter=1000), parametre, cv=5)
            self.predikcia(self.model)
        else:
            self.novaSprava("Najprv načítajte vstupy a ciele predikcie")

    def predikcia(self, model):
        self.novaSprava("Prebieha trénovanie modelu a predikcia...")
        QApplication.processEvents()
        try:
            if self.typ_dat == "statické":
                pocet_tren_dat = int(len(self.data_ciele) * (self.pomer_dat / 100))
                matica_ciela_tren = self.data_ciele[[self.zvoleny_ciel]].iloc[:pocet_tren_dat].copy()
                matica_ciela_test = self.data_ciele[[self.zvoleny_ciel]].iloc[pocet_tren_dat:].copy()

                # Škálovanie vstupných dát
                skalovanie = StandardScaler()
                y_tren = skalovanie.fit_transform(self.data_zvol_vstupy.iloc[:pocet_tren_dat])
                y_test = skalovanie.transform(self.data_zvol_vstupy.iloc[pocet_tren_dat:])

                # Trénovanie modelu
                model.fit(y_tren, matica_ciela_tren.values.ravel())
                # print(model.best_params_)

                # Predikcia na trénovacích aj testovacích dátach
                model_trenovane = model.predict(y_tren)
                model_testovacie = model.predict(y_test)

                # Príprava na export dát
                medzera = ([numpy.nan])
                self.merany_ciel = numpy.concatenate([matica_ciela_tren.values.ravel(), medzera, matica_ciela_test.values.ravel()])
                if self.zvoleny_ciel == "Uhlík (%)":
                    self.predikcia_uhlik = numpy.concatenate((model_trenovane, medzera, model_testovacie))
                elif self.zvoleny_ciel == "Teplota (°C)":
                    self.predikcia_teplota = numpy.concatenate((model_trenovane, medzera, model_testovacie))

                # Výpočet chýb
                mse_trenovane = mean_squared_error(matica_ciela_tren, model_trenovane)
                mse_testovacie = mean_squared_error(self.data_ciele.iloc[pocet_tren_dat:][self.zvoleny_ciel], model_testovacie)
                self.novaSprava(f"<b>Stredná kvadratická chyba (MSE) - trénované: {mse_trenovane: .4f}, testovacie: {mse_testovacie: .4f}</b>")

                x_tren = self.data_ciele.iloc[:len(model_trenovane)].index
                x_test = self.data_ciele.iloc[len(model_trenovane):].index

                real_tren = matica_ciela_tren.values.ravel()
                real_test = self.data_ciele.iloc[pocet_tren_dat:][self.zvoleny_ciel].values.ravel()
                abs_odchylka_tren = numpy.abs(real_tren - model_trenovane)
                abs_odchylka_test = numpy.abs(real_test - model_testovacie)
                abs_odchylka = numpy.concatenate((abs_odchylka_tren, abs_odchylka_test))
                abs_x = self.data_ciele.index
                for line in self.graf_ciele.get_lines():
                    if line.get_label() in ["Predikcia (trénované)", "Predikcia (testovacie)"]:
                        line.remove()
                for bar in getattr(self, "odchylka_bar", []):
                    bar.remove()
                if not hasattr(self, "graf_ciele_odchylka"):
                    self.graf_ciele_odchylka = self.graf_ciele.twinx()
                # Vykreslenie predikcií do grafu
                self.graf_ciele.plot(x_tren, model_trenovane, label="Predikcia (trénované)", color="green", linestyle="-", zorder=3)
                self.graf_ciele.plot(x_test, model_testovacie, label="Predikcia (testovacie)", color="orange", linestyle="-", zorder=3)
                self.odchylka_bar = self.graf_ciele_odchylka.bar(abs_x, abs_odchylka, width=1.0, alpha=0.25, color="gray", label="Absolútna odchýlka", zorder=1)
                self.graf_ciele_odchylka.bar(abs_x, abs_odchylka, width=1.0, alpha=0.25, color="gray", label="Absolútna odchýlka", zorder=1)
                self.graf_ciele.relim()
                self.graf_ciele.autoscale_view()
                self.graf_ciele_odchylka.relim()
                self.graf_ciele_odchylka.autoscale_view()
                self.graf_ciele_odchylka.grid(False)
                self.graf_ciele_odchylka.spines[:].set_visible(False)
                self.graf_ciele_odchylka.tick_params(axis='y', left=False, right=False, labelright=False)
                ciara_1, oznacenie_1 = self.graf_ciele.get_legend_handles_labels()
                ciara_2, oznacenie_2 = self.graf_ciele_odchylka.get_legend_handles_labels()

                # Zlúčiť a odstrániť duplicity podľa labelov
                vsetky_ciary = ciara_1 + ciara_2
                vsetky_oznacenia = oznacenie_1 + oznacenie_2
                legenda = dict(zip(vsetky_oznacenia, vsetky_ciary))  # zachová len posledné výskyty každého labelu

                self.graf_ciele.legend(legenda.values(), legenda.keys(), loc="lower left", bbox_to_anchor=(0, -0.32), ncol=10)

            elif self.typ_dat == "dynamické":
                spolocne_stlpce = list(set(self.data_zvol_vstupy.columns) & set(self.data_ciele.columns))
                self.zvolene_vstupy = [col for col in spolocne_stlpce if col not in ["Teplota (°C)", "Uhlík (%)"]]
                x_tren = self.data_vstupy[self.zvolene_vstupy]
                y_tren_teplota = self.data_vstupy["Teplota (°C)"]
                y_tren_uhlik = self.data_vstupy["Uhlík (%)"]
                x_test = self.data_ciele[self.zvolene_vstupy]
                skalovanie = StandardScaler()
                x_tren_skal = skalovanie.fit_transform(x_tren)
                x_test_skal = skalovanie.transform(x_test)
                model_teplota = clone(self.model)
                model_uhlik = clone(self.model)
                model_dyn_teplota = model_teplota.fit(x_tren_skal, y_tren_teplota.values.ravel())
                model_dyn_uhlik = model_uhlik.fit(x_tren_skal, y_tren_uhlik.values.ravel())
                self.predikcia_teplota = model_dyn_teplota.predict(x_test_skal)
                self.predikcia_uhlik = model_dyn_uhlik.predict(x_test_skal)
                self.resetGrafov()
                self.graf_pozorovania.set_title("Teplota (°C)", color=self.farba_popredia)
                self.graf_ciele.set_title("Uhlík (%)", color=self.farba_popredia)
                self.graf_pozorovania.plot(range(len(self.predikcia_teplota)), self.predikcia_teplota, label="Teplota (°C)", linestyle="-", zorder=2)
                self.graf_ciele.plot(range(len(self.predikcia_uhlik)), self.predikcia_uhlik, label="Uhlík (%)", linestyle="-", zorder=2)
                self.graf_pozorovania.margins(x=0)
                self.graf_ciele.margins(x=0)
        except ValueError as chyba:
            self.chybove_okno.showMessage(f"Neočakávané hodnoty:<br>{str(chyba)}")
            self.novaSprava(f"Neočakávané hodnoty v súbore {self.nazov_databazy}")
        except Exception as chyba:
            self.chybove_okno.showMessage(f"Neočakávaná chyba:<br>{str(chyba)}")
            self.novaSprava(f"Neočakávaná chyba pri otváraní súboru {self.nazov_databazy}")
        else:
            self.graf_ciele.figure.canvas.draw_idle()
            self.novaSprava("Predikcia dokončená")

    def pomocnik(self):
        cesta = os.path.abspath("uzivatelska_prirucka.pdf")

        if os.path.exists(cesta):
            webbrowser.open_new(cesta)
        else:
            self.chybove_okno.showMessage(f"Nepodarilo sa nájsť súbor: {cesta}")

    @staticmethod
    def o():
        o_aplikacii = ('Táto aplikácia bola vytvorená ako súčasť diplomovej práce "Predikcia teploty a uhlíka v procese výroby ocele na báze strojového učenia". '
                       'Umožňuje načítať namerané dáta z databázového súboru, vykresliť dáta do grafu, vykonať analýzu dáť a vytvoriť z nich model predikcie.')
        QMessageBox.about(QApplication.activeWindow(), "O aplikácií", o_aplikacii)

    def tmavyRezim(self, widget):
        palette = widget.palette()
        background = palette.color(QPalette.ColorRole.Window)
        darkmode = background.lightness() < 128  # 0 = čierna, 255 = biela

        if darkmode:
            self.farba_popredia = "white"
            self.farba_pozadia = "#2d2d2d"
        else:
            self.farba_popredia = "black"
            self.farba_pozadia = "white"

        self.graf_pozorovania.figure.subplots_adjust(left=0.05, right=0.83, hspace=0.25, top=0.94, bottom=0.11)
        self.graf_pozorovania.set_title('Pozorovania', color=self.farba_popredia)
        self.graf_pozorovania.figure.set_facecolor(self.farba_pozadia)
        self.graf_pozorovania.set_facecolor(self.farba_pozadia)
        self.graf_pozorovania.spines[:].set_color(self.farba_popredia)
        self.graf_pozorovania.tick_params(axis="both", colors=self.farba_popredia)
        self.graf_ciele.figure.subplots_adjust(left=0.05, right=0.83, hspace=0.25, top=0.94, bottom=0.11)
        self.graf_ciele.set_title('Ciele predikcie', color=self.farba_popredia)
        self.graf_ciele.set_facecolor(self.farba_pozadia)
        self.graf_ciele.spines[:].set_color(self.farba_popredia)
        self.graf_ciele.tick_params(axis="both", colors=self.farba_popredia)
        self.graf_ciele.yaxis.label.set_color(self.farba_popredia)


def main():

    app = QApplication([])
    window = HlavneOkno()
    window.show()
    app.exec()


if __name__ == '__main__': main()
