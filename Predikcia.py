### --- Importy štandardných knižníc ---
import os
import webbrowser

### --- Importy externých knižníc ---
import pandas
import seaborn
import numpy
from sklearn.base import clone
from sklearn.metrics import mean_squared_error
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
#from sklearn.model_selection import GridSearchCV

### --- Importy z lokálneho modulu ---
from nastavenia import (
    VseobecneNastavenia,
    NastaveniaVstupov,
    NastaveniaVystupov,
    NastaveniaModelu,
    DynTepUhlik
)

### --- Importy GUI komponentov ---
from PySide6.QtWidgets import (
    QApplication, QErrorMessage, QFileDialog, QGroupBox, QMainWindow, QMessageBox,
    QScrollArea, QSplitter, QTextEdit, QVBoxLayout, QWidget
)
from PySide6.QtGui import QPalette, QAction
from PySide6.QtCore import Qt

### --- Importy pre vizualizáciu ---
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
# noinspection PyPep8Naming

class HlavneOkno(QMainWindow):

    def __init__(self):
        super().__init__()

        # Deklarácia globálnych premenných
        self.data_vstupy = pandas.DataFrame()
        self.data_ciele = pandas.DataFrame()
        self.matica_ciela_test = pandas.DataFrame()
        self.nazov_databazy = ""
        self.chybove_okno = QErrorMessage(self)
        self.chybove_okno.setWindowTitle("Chyba")
        self.kodovanie = "windows-1250"
        self.oddelovac_dat = ";"
        self.pomer_dat = 70
        self.zvolene_vstupy = []
        self.vstupy_stlpce = []
        self.ciele_stlpce = []
        self.vstupy_checkboxy = []
        self.model = None
        self.stat_poz_nacitane = False
        self.ciel_dyn_poz_nacitane = False
        self.pocet_NN_vrstiev = (32, 16)
        self.oznacenie_stlpca_stat = "Tavba č."
        self.oznacenie_stlpca_dyn = "Čas (s)"
        self.oznacenie_teploty = "Teplota (°C)"
        self.oznacenie_uhlika = "Uhlík (%)"
        self.zvoleny_model = "SVR"
        self.zvoleny_kernel = "polynomická regresia"
        self.zvoleny_ciel = self.oznacenie_teploty
        self.typ_dat = ""
        self.os_x = ""
        self.predikcia_teplota = None
        self.predikcia_uhlik = None
        self.farba_popredia = "black"
        self.farba_pozadia = "white"
        self.data_zvol_vstupy = pandas.DataFrame()

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
        polozka_nacitat_vstupy = QAction("Načítať stat. pozorovania", self)
        polozka_nacitat_vstupy.triggered.connect(lambda: self.otvorit("vrchny"))
        menu_subor.addAction(polozka_nacitat_vstupy)
        polozka_nacitat_ciele = QAction("Načítať ciele / dyn. pozorovania", self)
        polozka_nacitat_ciele.triggered.connect(lambda: self.otvorit("spodny"))
        menu_subor.addAction(polozka_nacitat_ciele)
        polozka_export = QAction("Exportovať výsledky", self)
        polozka_export.triggered.connect(self.exportPredikcie)
        menu_subor.addAction(polozka_export)

        # Vytvorenie podmenu Nastavenia a jeho položiek
        polozka_nast_vseobecne = QAction("Všeobecné", self)
        polozka_nast_vseobecne.triggered.connect(self.vseobecneNastavenia)
        menu_nastavenia.addAction(polozka_nast_vseobecne)
        polozka_nast_vstupov = QAction("Pozorovania", self)
        polozka_nast_vstupov.triggered.connect(self.nastaveniaVstupov)
        menu_nastavenia.addAction(polozka_nast_vstupov)
        polozka_nast_vystupov = QAction("Ciele", self)
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

        # Rozvrhnutie grafov
        grafy = FigureCanvas(Figure(figsize=(5, 3)))
        grafy_roz = QVBoxLayout()
        grafy_roz.addWidget(NavigationToolbar(grafy, self))
        grafy_roz.addWidget(grafy)
        graf_zobrazenie = QGroupBox()
        graf_zobrazenie.setTitle("Grafy")
        graf_zobrazenie.setLayout(grafy_roz)
        self.graf_vrchny, self.graf_spodny = grafy.figure.subplots(2, 1)
        self.resetGrafov()

        # Hlavné vertikálne rozvrhnutie widgetov
        rozdelovac = QSplitter(Qt.Vertical)
        rozdelovac.addWidget(graf_zobrazenie)
        rozdelovac.addWidget(konzola)
        rozdelovac.setSizes([850, 150])
        rozlozenie = QVBoxLayout()
        rozlozenie.addWidget(rozdelovac)

        # Vytvorenie hlavného rámu aplikácie
        hlavny_frame = QWidget()
        hlavny_frame.setLayout(rozlozenie)
        self.setCentralWidget(hlavny_frame)

    # Zobrazenie novej správy v konzole
    def novaSprava(self, sprava):
        self.vystup_textu.append(sprava)

    # Vyčistenie zobrazenia grafov
    def resetGrafov(self):
        self.graf_vrchny.cla()
        self.graf_spodny.cla()
        self.graf_vrchny.grid(True)
        self.graf_spodny.grid(True)
        self.tmavyRezim(self)
        self.graf_vrchny.figure.canvas.draw_idle()
        self.graf_spodny.figure.canvas.draw_idle()

    # Otvorenie dát zo súboru
    def otvorit(self, dataframeIO):
        predvoleny_priecinok = os.path.abspath(os.getcwd())
        self.nazov_databazy, filtr = QFileDialog.getOpenFileName(
            None,
            "Otvoriť súbor",
            predvoleny_priecinok,
            "CSV súbory (*.csv);;Súbory programu Microsoft Excel (*.xlsx *.xls *.xlsb *.xlsm);;"
            "Súbory typu OpenDocument (*.ods);;Textové súbory (*.txt);;Všetky súbory (*.*)"
        )

        if self.nazov_databazy:
            try:
                _, pripona_suboru = os.path.splitext(self.nazov_databazy)
                pripona_suboru = pripona_suboru.lower()

                if pripona_suboru in [".csv", ".txt"]:
                    dataframe = pandas.read_csv(
                        self.nazov_databazy,
                        delimiter=self.oddelovac_dat,
                        encoding=self.kodovanie,
                        header=0
                    )
                elif pripona_suboru in [".xlsx", ".xls", ".ods", ".xlsb", ".xlsm"]:
                    dataframe = pandas.read_excel(self.nazov_databazy, engine="calamine")
                else:
                    raise ValueError("Nepodporovaný formát súboru")

                self.novaSprava(f"Súbor {self.nazov_databazy} bol úspešne otvorený")
                pocet_stlpcov = None
                pocet_riadkov = None

                if dataframeIO == "vrchny":
                    if self.stat_poz_nacitane and self.ciel_dyn_poz_nacitane:
                        self.data_ciele = pandas.DataFrame()
                        self.resetGrafov()
                        self.ciel_dyn_poz_nacitane = False
                        self.zvolene_vstupy = []
                    self.data_vstupy = dataframe
                    pocet_riadkov, pocet_stlpcov = self.data_vstupy.shape
                    pocet_riadkov -= 1
                elif dataframeIO == "spodny":
                    if self.stat_poz_nacitane and self.ciel_dyn_poz_nacitane:
                        self.data_vstupy = pandas.DataFrame()
                        self.resetGrafov()
                        self.stat_poz_nacitane = False
                        self.zvolene_vstupy = []
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
                if dataframeIO == "vrchny":
                    self.vykresliVrchnyGraf()
                elif dataframeIO == "spodny":
                    self.vykresliSpodnyGraf()

    def zvoleneVstupy(self):
        spolocne_stlpce = list(set(self.vstupy_stlpce) & set(self.ciele_stlpce))
        self.zvolene_vstupy = [col for col in spolocne_stlpce if col not in [self.oznacenie_teploty, self.oznacenie_uhlika]]

    def vykresliVrchnyGraf(self):
        # Vyčistenie a príprava grafu pre statické vstupné dáta
        self.graf_vrchny.cla()
        self.tmavyRezim(self)
        self.graf_vrchny.set_title('Statické pozorovania', color=self.farba_popredia)
        self.graf_vrchny.grid(True)

        self.vstupy_stlpce = self.data_vstupy.columns[:].tolist()

        # Identifikácia osy X na základe známeho názvu stĺpca
        print(f"self.vstupy_stlpce:\n{self.vstupy_stlpce}")
        if self.oznacenie_stlpca_stat in self.vstupy_stlpce:
            self.os_x = self.oznacenie_stlpca_stat
        elif self.oznacenie_stlpca_dyn in self.vstupy_stlpce:
            self.os_x = self.oznacenie_stlpca_dyn
        else:
            self.data_vstupy.reset_index(inplace=True)
            self.os_x = "index"
            self.vstupy_stlpce = self.data_vstupy.columns[:].tolist()

        if not self.data_vstupy.empty and not self.data_ciele.empty and not self.zvolene_vstupy and self.typ_dat == "dynamické":
            self.zvoleneVstupy()
        vykreslene_vstupy = self.zvolene_vstupy if self.zvolene_vstupy else self.vstupy_stlpce[1:]
        if self.os_x not in vykreslene_vstupy:
            vykreslene_vstupy = [self.os_x] + vykreslene_vstupy
        self.data_zvol_vstupy = self.data_vstupy[vykreslene_vstupy].copy()

        # Preusporiadanie dát pre vizualizáciu
        nac_data_vstupy = self.data_zvol_vstupy.melt(
            id_vars=self.os_x,
            var_name="Názov stĺpca",
            value_name=""
        )

        plot1 = seaborn.lineplot(
            data=nac_data_vstupy,
            x=self.os_x,
            y="",
            hue="Názov stĺpca",
            ax=self.graf_vrchny
        )
        plot1.legend(loc="upper left", bbox_to_anchor=(1.01, 1.1))
        plot1.set_xlabel(self.os_x, labelpad=-10, x=-0.03, color=self.farba_popredia)

        xlim_max = self.data_vstupy.index.max()
        plot1.set_xlim(0, xlim_max)
        self.graf_vrchny.figure.canvas.draw_idle()

        if "index" in self.data_vstupy.columns:
            self.data_vstupy.drop(columns=["index"], inplace=True)
        self.stat_poz_nacitane = True

    def vykresliSpodnyGraf(self):
        # Vyčistenie a príprava grafu pre dynamické pozorovania
        self.graf_spodny.cla()
        self.tmavyRezim(self)
        self.graf_spodny.grid(True)

        self.ciele_stlpce = self.data_ciele.columns[:].tolist()
        nac_data_ciele = pandas.DataFrame()
        plot2 = seaborn.lineplot()

        # Spracovanie statických cieľov
        if self.oznacenie_stlpca_stat in self.ciele_stlpce:
            self.typ_dat = "statické"
            self.novaSprava("Zistené statické dáta")
            self.graf_spodny.set_title('Cieľ predikcie', color=self.farba_popredia)
            self.os_x = self.oznacenie_stlpca_stat

            if self.zvoleny_ciel == self.oznacenie_teploty:
                nac_data_ciele = self.data_ciele.melt(
                    id_vars=self.os_x,
                    value_vars=self.oznacenie_teploty,
                    var_name="Teplota",
                    value_name="(°C)"
                )
                plot2 = seaborn.lineplot(
                    data=nac_data_ciele,
                    x=self.os_x,
                    y="(°C)",
                    hue="Teplota",
                    ax=self.graf_spodny,
                    color="dodgerblue"
                )

            elif self.zvoleny_ciel == self.oznacenie_uhlika:
                nac_data_ciele = self.data_ciele.melt(
                    id_vars=self.os_x,
                    value_vars=self.oznacenie_uhlika,
                    var_name="Koncentrácia uhlíka",
                    value_name="(%)"
                )
                plot2 = seaborn.lineplot(
                    data=nac_data_ciele,
                    x=self.os_x,
                    y="(%)",
                    hue="Koncentrácia uhlíka",
                    ax=self.graf_spodny,
                    color="dodgerblue"
                )

            plot2.legend(loc="lower left", bbox_to_anchor=(0, -0.30), ncol=10)

        # Spracovanie dynamických cieľov
        elif self.oznacenie_stlpca_dyn in self.ciele_stlpce:
            self.typ_dat = "dynamické"
            self.novaSprava("Zistené dynamické dáta")

            if hasattr(self, "odchylka_bar"):
                for bar in self.odchylka_bar:
                    bar.remove()
                del self.odchylka_bar

            if hasattr(self, "graf_ciele_odchylka"):
                self.graf_ciele_odchylka.cla()
                self.graf_ciele_odchylka.remove()
                del self.graf_ciele_odchylka

            self.graf_spodny.set_title('Dynamické pozorovania', color=self.farba_popredia)
            self.os_x = self.oznacenie_stlpca_dyn

            if self.ciele_stlpce and self.vstupy_stlpce and not self.zvolene_vstupy:
                self.zvoleneVstupy()

            if self.stat_poz_nacitane == True and self.ciel_dyn_poz_nacitane == False and self.zvolene_vstupy:
                spolocne_stlpce = list(set(self.zvolene_vstupy) & set(self.ciele_stlpce))
                self.zvolene_vstupy = [col for col in spolocne_stlpce if col not in [self.oznacenie_teploty, self.oznacenie_uhlika]]
            print(f"stat poz / ciel dyn poz / zvol vstupy / ciele stlpce:\n{self.stat_poz_nacitane, self.ciel_dyn_poz_nacitane, self.zvolene_vstupy, self.ciele_stlpce}")
            if self.stat_poz_nacitane == False and not self.zvolene_vstupy:
                self.zvolene_vstupy = self.ciele_stlpce[1:]
            vykreslene_ciele = self.zvolene_vstupy
            if self.os_x not in vykreslene_ciele:
                vykreslene_ciele = [self.os_x] + vykreslene_ciele

            print(f"vykreslene ciele:\n{vykreslene_ciele}")
            self.data_zvol_ciele = self.data_ciele[vykreslene_ciele].copy()
            nac_data_ciele = self.data_zvol_ciele.melt(
                id_vars=self.os_x,
                var_name="Názov stĺpca",
                value_name=""
            )

            plot2 = seaborn.lineplot(
                data=nac_data_ciele,
                x=self.os_x,
                y="",
                hue="Názov stĺpca",
                ax=self.graf_spodny,
                color="blue"
            )
            plot2.legend(loc="lower left", bbox_to_anchor=(-0.05, -0.30), ncol=11)

        else:
            self.novaSprava("Nezistený typ dát")
            self.chybove_okno.showMessage(
                "Nezistený typ dát.<br>Nie je možné rozpoznať stĺpec s časom alebo por. číslami tavieb."
            )

        # Nastavenie popisov a rozsahov grafu
        plot2.set_xlabel(self.os_x, labelpad=-10, x=-0.03, color=self.farba_popredia)
        xlim_max = nac_data_ciele[self.os_x].max()
        print(f"os_x / nac dat ciele / xlim max:\n{self.os_x, nac_data_ciele, xlim_max}")
        plot2.set_xlim(0, xlim_max)
        self.graf_spodny.figure.canvas.draw_idle()
        self.ciel_dyn_poz_nacitane = True

    def exportPredikcie(self):
        dataframe_predikcia = pandas.DataFrame()
        if self.predikcia_uhlik is not None or self.predikcia_teplota is not None:
            file_path, _ = QFileDialog.getSaveFileName(None, "Exportovať dáta", "", "CSV súbory (*.csv);;Všetky súbory (*)")
            if file_path:
                data = {}
                if self.typ_dat == "statické":
                    if self.zvoleny_ciel == self.oznacenie_teploty:
                        data["Meraná teplota (°C)"] = self.merany_ciel
                    if self.zvoleny_ciel == self.oznacenie_uhlika:
                        data["Meraný uhlík (%)"] = self.merany_ciel
                if self.predikcia_teplota is not None and len(self.predikcia_teplota) > 0:
                    data["Predikovaná teplota (°C)"] = self.predikcia_teplota
                if self.predikcia_uhlik is not None and len(self.predikcia_uhlik) > 0:
                    data["Predikovaný uhlík (%)"] = self.predikcia_uhlik
                if data: dataframe_predikcia = pandas.DataFrame(data)
                # Uloženie do CSV
                dataframe_predikcia.to_csv(file_path, index=False, sep=self.oddelovac_dat, encoding=self.kodovanie)
                self.novaSprava(f"Výsledky predikcie s využitím modelu {self.zvoleny_model} boli uložené do priečinku {file_path}")
                if self.typ_dat == "statické": self.novaSprava("-Trénovacia a testovacia časť statických dát je oddelená prázdnym riadkom-")
        else:
            self.novaSprava("Žiadne dáta na export. Najprv vykonajte predikciu.")

    # Voľba modelu predikcie a nastavenie parametrov
    def volbaModelu(self):
        if self.ciel_dyn_poz_nacitane and self.stat_poz_nacitane:
            model_mapa = {
                "SVR": SVR(kernel='rbf', C=20, epsilon=0.001),
                "RF": RandomForestRegressor(random_state=17, n_jobs=-1),
                "NN": MLPRegressor(hidden_layer_sizes=self.pocet_NN_vrstiev, solver="lbfgs", learning_rate="adaptive", alpha=0.0001, max_iter=200, random_state=17)
                          }
            self.model = model_mapa.get(self.zvoleny_model)

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
            self.novaSprava("Najprv načítajte pozorovania a ciele predikcie")

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
                #print(model.best_params_)

                # Predikcia na trénovacích aj testovacích dátach
                model_trenovane = model.predict(y_tren)
                model_testovacie = model.predict(y_test)

                # Príprava na export dát
                medzera = ([numpy.nan])
                self.merany_ciel = numpy.concatenate([matica_ciela_tren.values.ravel(), medzera, matica_ciela_test.values.ravel()])
                if self.zvoleny_ciel == self.oznacenie_uhlika:
                    self.predikcia_uhlik = numpy.concatenate((model_trenovane, medzera, model_testovacie))
                elif self.zvoleny_ciel == self.oznacenie_teploty:
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
                for line in self.graf_spodny.get_lines():
                    if line.get_label() in ["Predikcia (trénované)", "Predikcia (testovacie)"]:
                        line.remove()
                if hasattr(self, "odchylka_bar"):
                    for bar in self.odchylka_bar:
                        bar.remove()
                if not hasattr(self, "graf_ciele_odchylka"):
                    self.graf_ciele_odchylka = self.graf_spodny.twinx()
                self.graf_spodny.plot(x_tren, model_trenovane, label="Predikcia (trénované)", color="green", linestyle="-", zorder=3)
                self.graf_spodny.plot(x_test, model_testovacie, label="Predikcia (testovacie)", color="orange", linestyle="-", zorder=3)
                self.odchylka_bar = self.graf_ciele_odchylka.bar(abs_x, abs_odchylka, width=1.0, alpha=0.25, color="gray", label="Absolútna odchýlka", zorder=1)
                self.graf_spodny.relim()
                self.graf_spodny.autoscale_view()
                self.graf_ciele_odchylka.relim()
                self.graf_ciele_odchylka.autoscale_view()
                self.graf_ciele_odchylka.grid(False)
                self.graf_ciele_odchylka.spines[:].set_visible(False)
                self.graf_ciele_odchylka.tick_params(axis='y', left=False, right=False, labelright=False)
                ciara_1, oznacenie_1 = self.graf_spodny.get_legend_handles_labels()
                ciara_2, oznacenie_2 = self.graf_ciele_odchylka.get_legend_handles_labels()
                vsetky_ciary = ciara_1 + ciara_2
                vsetky_oznacenia = oznacenie_1 + oznacenie_2
                legenda = dict(zip(vsetky_oznacenia, vsetky_ciary))  # zachová len posledné výskyty každého labelu
                self.graf_spodny.legend(legenda.values(), legenda.keys(), loc="lower left", bbox_to_anchor=(0, -0.32), ncol=10)

            elif self.typ_dat == "dynamické":
                merane = {"teplota_zac": None,"teplota_konc": None,"uhlik_zac": None,"uhlik_konc": None}
                dialog = DynTepUhlik(self)
                if dialog.exec():
                    merane = dialog.vysledky
                spolocne_stlpce = list(set(self.data_zvol_vstupy.columns) & set(self.data_ciele.columns))
                self.zvolene_vstupy = [col for col in spolocne_stlpce if col not in [self.oznacenie_teploty, self.oznacenie_uhlika]]
                x_tren = self.data_vstupy[self.zvolene_vstupy]
                y_tren_teplota = self.data_vstupy[self.oznacenie_teploty]
                y_tren_uhlik = self.data_vstupy[self.oznacenie_uhlika]
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
                self.graf_vrchny.set_title("Predikovaná teplota (°C)", color=self.farba_popredia)
                self.graf_spodny.set_title("Predikovaný uhlík (%)", color=self.farba_popredia)
                self.graf_vrchny.plot(range(len(self.predikcia_teplota)), self.predikcia_teplota, label=self.oznacenie_teploty, linestyle="-", zorder=2, color="red")
                self.graf_spodny.plot(range(len(self.predikcia_uhlik)), self.predikcia_uhlik, label=self.oznacenie_uhlika, linestyle="-", zorder=2, color="dodgerblue")
                if merane["teplota_zac"] is not None:
                    self.graf_vrchny.plot(0, merane["teplota_zac"], marker="o", color="darkorange", label="Meraná zač. teplota (°C)", zorder=4)
                if merane["teplota_konc"] is not None:
                    self.graf_vrchny.plot(len(self.predikcia_teplota) - 1, merane["teplota_konc"], marker="o", color="gold", label="Meraná konc. teplota (°C)", zorder=4)
                if merane["uhlik_zac"] is not None:
                    self.graf_spodny.plot(0, merane["uhlik_zac"], marker="o", color="mediumspringgreen", label="Meraná zač. koncentrácia uhlíka (%)", zorder=4)
                if merane["uhlik_konc"] is not None:
                    self.graf_spodny.plot(len(self.predikcia_uhlik) - 1, merane["uhlik_konc"], marker="o", color="darkturquoise", label="Meraná kon. koncentrácia uhlíka (%)", zorder=4)
                self.graf_vrchny.set_xlabel(self.oznacenie_stlpca_dyn, labelpad=-10, x=-0.03, color=self.farba_popredia)
                self.graf_spodny.set_xlabel(self.oznacenie_stlpca_dyn, labelpad=-10, x=-0.03, color=self.farba_popredia)
                self.graf_vrchny.set_ylabel("(°C)", color=self.farba_popredia)
                self.graf_spodny.set_ylabel("(%)", color=self.farba_popredia)
                self.graf_vrchny.margins(x=0)
                self.graf_spodny.margins(x=0)
                self.graf_vrchny.legend(loc="upper left", bbox_to_anchor=(1.01, 1.1))
                self.graf_spodny.legend(loc="upper left", bbox_to_anchor=(1.01, 1.1))
        except ValueError as chyba:
            self.chybove_okno.showMessage(f"Neočakávané hodnoty:<br>{str(chyba)}")
            self.novaSprava(f"Neočakávané hodnoty v súbore {self.nazov_databazy}")
        except Exception as chyba:
            self.chybove_okno.showMessage(f"Neočakávaná chyba:<br>{str(chyba)}")
            self.novaSprava(f"Neočakávaná chyba pri otváraní súboru {self.nazov_databazy}")
        else:
            self.graf_spodny.figure.canvas.draw_idle()
            self.novaSprava("Predikcia dokončená")

    def pomocnik(self):
        cesta = os.path.abspath("uzivatelska_prirucka.pdf")
        if os.path.exists(cesta):
            webbrowser.open_new(cesta)
        else:
            self.chybove_okno.showMessage(f"Nepodarilo sa nájsť súbor: {cesta}")

    # Nastavenie farebného motívu
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

        self.graf_vrchny.figure.subplots_adjust(left=0.05, right=0.83, hspace=0.25, top=0.94, bottom=0.11)
        self.graf_vrchny.set_title('Statické pozorovania', color=self.farba_popredia)
        self.graf_vrchny.figure.set_facecolor(self.farba_pozadia)
        self.graf_vrchny.set_facecolor(self.farba_pozadia)
        self.graf_vrchny.spines[:].set_color(self.farba_popredia)
        self.graf_vrchny.tick_params(axis="both", colors=self.farba_popredia)
        self.graf_spodny.figure.subplots_adjust(left=0.05, right=0.83, hspace=0.25, top=0.94, bottom=0.11)
        self.graf_spodny.set_facecolor(self.farba_pozadia)
        self.graf_spodny.spines[:].set_color(self.farba_popredia)
        self.graf_spodny.tick_params(axis="both", colors=self.farba_popredia)
        self.graf_spodny.yaxis.label.set_color(self.farba_popredia)

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
        if self.zvoleny_ciel == self.oznacenie_teploty:
            self.novaSprava(f"{self.oznacenie_teploty} bola nastavená ako cieľ predikcie")
        elif self.zvoleny_ciel == self.oznacenie_uhlika:
            self.novaSprava(f"{self.oznacenie_uhlika} bol nastavený ako cieľ predikcie")

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

    @staticmethod
    def o():
        o_aplikacii = (
            'Táto aplikácia bola vytvorená ako súčasť diplomovej práce "Predikcia teploty a uhlíka v procese výroby ocele na báze strojového učenia". '
            'Umožňuje načítať namerané dáta z databázového súboru, vykresliť dáta do grafu, vykonať analýzu dáť a vytvoriť z nich model predikcie.')
        QMessageBox.about(QApplication.activeWindow(), "O aplikácií", o_aplikacii)


def main():
    app = QApplication([])
    window = HlavneOkno()
    window.show()
    app.exec()
if __name__ == '__main__': main()
