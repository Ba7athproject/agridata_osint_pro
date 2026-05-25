import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import requests
import pandas as pd
import threading
import os
import re
import time 

# Configuration de l'apparence professionnelle
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AgridataProApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Agridata OSINT Explorer - Projet Ba7ath")
        self.geometry("1000x750")
        self.minsize(900, 700)

        self.selected_resource_id = None
        self.current_search_results = [] 
        self.api_base_url = "https://catalog.agridata.tn/fr/api/3/action"
        
        # Liste exhaustive des gouvernorats pour l'investigation régionale
        self.gouvernorats_tn = [
            "Ariana", "Béja", "Ben Arous", "Bizerte", "Gabès", "Gafsa", 
            "Jendouba", "Kairouan", "Kasserine", "Kébili", "Le Kef", "Mahdia", 
            "La Manouba", "Médenine", "Monastir", "Nabeul", "Sfax", "Sidi Bouzid", 
            "Siliana", "Sousse", "Tataouine", "Tozeur", "Tunis", "Zaghouan"
        ]

        self._build_ui()

    def _build_ui(self):
        """Construit l'interface graphique modulaire et les champs de recherche."""
        # ================= PANNEAU GAUCHE : RECHERCHE ET FILTRES =================
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)

        ctk.CTkLabel(self.sidebar, text="🔍 Recherche Avancée", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 10), padx=20)
        
        # 1. Mots-clés
        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Mots-clés (ex: cheptel, eau...)", width=280)
        self.search_entry.pack(pady=5, padx=20)
        self.search_entry.bind("<Return>", lambda event: self.start_search())

        # 2. Filtres Temporels (Années)
        ctk.CTkLabel(self.sidebar, text="Période (Années) :", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20, pady=(10, 0))
        self.date_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.date_frame.pack(pady=5, padx=20, fill="x")
        
        self.entry_year_start = ctk.CTkEntry(self.date_frame, placeholder_text="De (ex: 2019)", width=130)
        self.entry_year_start.pack(side="left")
        self.entry_year_end = ctk.CTkEntry(self.date_frame, placeholder_text="À (ex: 2023)", width=130)
        self.entry_year_end.pack(side="right")

        # 3. Filtres Géographiques (Gouvernorats)
        ctk.CTkLabel(self.sidebar, text="Gouvernorats :", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20, pady=(10, 0))
        
        # Bouton Tout sélectionner / Désélectionner
        self.chk_select_all_var = ctk.StringVar(value="")
        self.chk_select_all = ctk.CTkCheckBox(self.sidebar, text="Tout sélectionner", 
                                              variable=self.chk_select_all_var, 
                                              onvalue="ALL", offvalue="", 
                                              command=self.toggle_all_govs)
        self.chk_select_all.pack(anchor="w", padx=25, pady=(0, 5))

        self.gov_frame = ctk.CTkScrollableFrame(self.sidebar, height=120, width=280)
        self.gov_frame.pack(pady=5, padx=20)
        
        self.gov_vars = {}
        for gov in self.gouvernorats_tn:
            var = ctk.StringVar(value="")
            chk = ctk.CTkCheckBox(self.gov_frame, text=gov, variable=var, onvalue=gov, offvalue="", checkbox_height=18, checkbox_width=18)
            chk.pack(anchor="w", pady=2, padx=5)
            self.gov_vars[gov] = var

        # Bouton de lancement de recherche
        self.btn_search = ctk.CTkButton(self.sidebar, text="Lancer la recherche", command=self.start_search)
        self.btn_search.pack(pady=10, padx=20, fill="x")

        # 4. Zone des résultats
        ctk.CTkLabel(self.sidebar, text="Résultats trouvés :", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5, 5), padx=20, anchor="w")
        self.results_frame = ctk.CTkScrollableFrame(self.sidebar, width=280)
        self.results_frame.pack(pady=5, padx=20, fill="both", expand=True)

        # NOUVEAU : Bouton Télécharger TOUT (Lot)
        self.btn_download_all = ctk.CTkButton(self.sidebar, text="📥 Télécharger TOUT (Lot)", 
                                              font=ctk.CTkFont(weight="bold"),
                                              fg_color="#8e44ad", hover_color="#9b59b6", 
                                              state="disabled", command=self.start_batch_extraction)
        self.btn_download_all.pack(pady=15, padx=20, fill="x")

        # ================= PANNEAU DROIT : EXTRACTION ET LOGS =================
        self.main_panel = ctk.CTkFrame(self, corner_radius=10)
        self.main_panel.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.main_panel, text="Tableau de Bord d'Extraction", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 5))
        self.lbl_selected = ctk.CTkLabel(self.main_panel, text="Aucun dataset sélectionné.", text_color="gray")
        self.lbl_selected.pack(pady=(0, 20))

        # Bouton d'aperçu rapide 
        self.btn_preview = ctk.CTkButton(self.main_panel, text="👁️ Aperçu rapide (5 lignes)", 
                                         font=ctk.CTkFont(size=14, weight="bold"), height=35,
                                         fg_color="#e67e22", hover_color="#d35400",
                                         state="disabled", command=self.start_preview)
        self.btn_preview.pack(pady=(0, 10))

        # Bouton d'extraction individuelle 
        self.btn_extract = ctk.CTkButton(self.main_panel, text="📥 Télécharger le Dataset sélectionné", 
                                         font=ctk.CTkFont(size=15, weight="bold"), height=40,
                                         state="disabled", command=self.start_extraction)
        self.btn_extract.pack(pady=10)

        # Barre de progression
        self.progress_bar = ctk.CTkProgressBar(self.main_panel, width=400)
        self.progress_bar.pack(pady=15)
        self.progress_bar.set(0)

        # Console de logs
        self.log_box = ctk.CTkTextbox(self.main_panel, width=500, height=300, font=("Consolas", 12))
        self.log_box.pack(pady=10, padx=20, fill="both", expand=True)
        self.log_box.insert("0.0", "Bienvenue dans l'explorateur universel Agridata.\nConfigurez vos filtres et lancez une recherche...\n")
        self.log_box.configure(state="disabled")

    # ================= LOGIQUE D'INTERFACE =================
    def toggle_all_govs(self):
        """Coche ou décoche tous les gouvernorats."""
        state = self.chk_select_all_var.get()
        for gov, var in self.gov_vars.items():
            if state == "ALL":
                var.set(gov)
            else:
                var.set("")

    def log(self, message):
        """Affiche les messages dans la console intégrée (Thread-safe)."""
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _update_progress(self, val):
        """Met à jour la barre de progression (Thread-safe)."""
        self.progress_bar.set(val)

    # ================= LOGIQUE DE RECHERCHE =================
    def start_search(self):
        query = self.search_entry.get().strip()
        
        if not query:
            self.log("⚠️ Veuillez entrer au moins un mot-clé de recherche (ex: cheptel).")
            return

        # Réinitialisation
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.current_search_results.clear()
        self.btn_download_all.configure(state="disabled")

        self.log(f"\n--- Recherche en cours ---")
        self.log(f"Requête API (Mots-clés) : '{query}'")
        self.btn_search.configure(state="disabled")
        
        threading.Thread(target=self._fetch_search_results, args=(query,), daemon=True).start()

    def _fetch_search_results(self, query):
        url = f"{self.api_base_url}/package_search"
        params = {'q': query, 'rows': 50} 

        try:
            # Timeout (10s max pour connecter, 20s max sans réponse)
            response = requests.get(url, params=params, timeout=(10, 20))
            response.raise_for_status()
            data = response.json()

            results = data.get('result', {}).get('results', [])
            found_resources = 0

            for dataset in results:
                dataset_title = dataset.get('title', 'Dataset sans titre')
                for resource in dataset.get('resources', []):
                    if resource.get('datastore_active'):
                        found_resources += 1
                        res_name = resource.get('name', 'Ressource')
                        res_id = resource.get('id')
                        
                        self.current_search_results.append({
                            "title": dataset_title,
                            "res_name": res_name,
                            "res_id": res_id
                        })
                        
                        self.after(0, self._add_result_button, dataset_title, res_name, res_id)

            if found_resources == 0:
                self.log("❌ Aucun dataset tabulaire trouvé pour ces critères.")
            else:
                self.log(f"✅ {found_resources} ressource(s) exploitable(s) trouvée(s).")
                self.after(0, lambda: self.btn_download_all.configure(state="normal", text=f"📥 Télécharger les {found_resources} fichiers"))

        except Exception as e:
            self.log(f"❌ Erreur réseau ou API : {str(e)}")
        finally:
            self.after(0, lambda: self.btn_search.configure(state="normal"))

    def _add_result_button(self, dataset_title, res_name, res_id):
        btn_text = f"📁 {dataset_title[:35]}...\n↳ {res_name}"
        btn = ctk.CTkButton(self.results_frame, text=btn_text, fg_color="#2c3e50", hover_color="#34495e",
                            anchor="w", command=lambda: self.select_resource(dataset_title, res_name, res_id))
        btn.pack(pady=5, padx=5, fill="x")

    def select_resource(self, dataset_title, res_name, res_id):
        self.selected_resource_id = res_id
        self.lbl_selected.configure(text=f"Sélection : {dataset_title}\n({res_name})", text_color="#2ecc71")
        self.btn_extract.configure(state="normal")
        self.btn_preview.configure(state="normal")
        self.log(f"Dataset prêt pour l'extraction. ID : {res_id}")

    # ================= LOGIQUE D'APERÇU (PREVIEW) =================
    def start_preview(self):
        if not self.selected_resource_id:
            return
        self.btn_preview.configure(state="disabled")
        threading.Thread(target=self._fetch_preview, args=(self.selected_resource_id,), daemon=True).start()

    def _fetch_preview(self, resource_id):
        url = f"{self.api_base_url}/datastore_search"
        params = {'resource_id': resource_id, 'limit': 5} 

        try:
            self.log(f"\n--- Récupération de l'aperçu... ---")
            response = requests.get(url, params=params, timeout=(10, 20))
            response.raise_for_status()

            records = response.json().get('result', {}).get('records', [])
            if not records:
                self.log("⚠️ Le dataset est vide sur le serveur.")
                return

            df = pd.DataFrame(records)
            cols_to_check = [col for col in df.columns if col != '_id']
            df = df.dropna(subset=cols_to_check, how='all')

            self.after(0, self._show_preview_popup, df)

        except Exception as e:
            self.log(f"❌ Erreur lors de l'aperçu : {str(e)}")
        finally:
            self.after(0, lambda: self.btn_preview.configure(state="normal"))

    def _show_preview_popup(self, df):
        popup = ctk.CTkToplevel(self)
        popup.title("Aperçu des données brutes (OSINT)")
        popup.geometry("850x350")
        popup.attributes("-topmost", True)

        ctk.CTkLabel(popup, text="Structure des 5 premières lignes :", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        txt = ctk.CTkTextbox(popup, font=("Consolas", 12), wrap="none")
        txt.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        txt.insert("0.0", df.to_string(index=False))
        txt.configure(state="disabled")
        
        self.log("✅ Aperçu affiché. Vérifiez la structure des colonnes.")

    # ================= LOGIQUE D'EXTRACTION DE MASSE (BATCH) =================
    def start_batch_extraction(self):
        if not self.current_search_results:
            return
        
        directory = filedialog.askdirectory(title="Choisir le dossier de destination pour le téléchargement en lot")
        if not directory:
            return

        self.btn_download_all.configure(state="disabled")
        self.btn_extract.configure(state="disabled")
        self.progress_bar.set(0)
        
        threading.Thread(target=self._batch_extract_data, args=(directory,), daemon=True).start()

    def _sanitize_filename(self, filename):
        clean = re.sub(r'[\\/*?:"<>|]', "-", filename)
        return clean[:100] 

    def _batch_extract_data(self, directory):
        total_files = len(self.current_search_results)
        self.log(f"\n🚀 DÉBUT DU TÉLÉCHARGEMENT EN LOT ({total_files} fichiers) vers {directory}")

        for index, item in enumerate(self.current_search_results, start=1):
            res_id = item["res_id"]
            raw_title = f"{item['title']} - {item['res_name']}"
            safe_filename = self._sanitize_filename(raw_title) + ".csv"
            filepath = os.path.join(directory, safe_filename)

            self.log(f"\n[{index}/{total_files}] Traitement de : {safe_filename[:50]}...")
            self.after(0, self._update_progress, index / total_files)

            time.sleep(2.5)

            try:
                df = self._core_extraction_engine(res_id, update_ui_progress=False)
            except Exception as e:
                self.log(f"   ↳ ❌ Crash fatal intercepté : {str(e)}. Passage au suivant.")
                df = None
            
            if df is None:
                self.log("   ↳ ⏭️ Fichier ignoré suite à une erreur réseau ou un blocage API. Passage au suivant.")
                continue 

            if not df.empty:
                try:
                    df.to_csv(filepath, index=False, encoding='utf-8-sig')
                    self.log(f"   ↳ 💾 Sauvegardé ({len(df)} lignes).")
                except Exception as e:
                    self.log(f"   ↳ ❌ Erreur de sauvegarde locale : {str(e)}")
            else:
                self.log("   ↳ ⚠️ Fichier vide ou filtré entièrement. Ignoré.")

        self.log(f"\n🎉 TÉLÉCHARGEMENT EN LOT TERMINÉ !")
        self.after(0, lambda: self.btn_download_all.configure(state="normal"))
        self.after(0, lambda: self.btn_extract.configure(state="normal" if self.selected_resource_id else "disabled"))

    # ================= MOTEUR D'EXTRACTION CENTRAL (Individuel & Lot) =================
    def start_extraction(self):
        if not self.selected_resource_id:
            return
        
        self.btn_extract.configure(state="disabled")
        self.progress_bar.set(0)
        
        def run_single():
            df = self._core_extraction_engine(self.selected_resource_id, update_ui_progress=True)
            if df is not None and not df.empty:
                self.after(0, self._save_file_dialog, df)
            else:
                self.log("⚠️ Opération annulée, fichier vide ou erreur API.")
            self.after(0, lambda: self.btn_extract.configure(state="normal"))
            
        threading.Thread(target=run_single, daemon=True).start()

    def _core_extraction_engine(self, resource_id, update_ui_progress=False):
        url = f"{self.api_base_url}/datastore_search"
        # [FIX] Réduction de la limite par lot pour soulager le serveur (de 1000 à 500)
        limit = 500
        offset = 0
        all_records = []

        try:
            with requests.Session() as session:
                # [FIX] Tuple Timeout : (10s pour se connecter, 45s d'attente maximum sans recevoir de données)
                res = session.get(url, params={'resource_id': resource_id, 'limit': 0}, timeout=(10, 45))
                res.raise_for_status()
                
                try:
                    data = res.json()
                except ValueError:
                    self.log("   ↳ ❌ Erreur : Le serveur a renvoyé un format invalide (HTML).")
                    return None

                total_records = data.get('result', {}).get('total', 0)
                
                if total_records == 0:
                    return None

                while offset < total_records:
                    params = {'resource_id': resource_id, 'limit': limit, 'offset': offset}
                    
                    # [FIX] Traceur visuel ajouté pour surveiller précisément là où ça bloque
                    current_max = min(offset + limit, total_records)
                    self.log(f"   ↳ ⏳ API Call : Récupération des lignes {offset} à {current_max}/{total_records}...")

                    # [FIX] Timeout tuple renforcé ici aussi
                    batch_res = session.get(url, params=params, timeout=(10, 45))
                    batch_res.raise_for_status()
                    
                    try:
                        batch_data = batch_res.json()
                    except ValueError:
                        self.log("   ↳ ❌ Erreur en cours de téléchargement (données corrompues). Arrêt propre.")
                        break 
                        
                    batch = batch_data.get('result', {}).get('records', [])
                    if not batch: break
                        
                    all_records.extend(batch)
                    offset += limit

                    if update_ui_progress:
                        progress = min(len(all_records) / total_records, 1.0)
                        self.after(0, self._update_progress, progress)

        except requests.exceptions.Timeout:
            self.log(f"   ↳ ❌ Délai dépassé (Silent Hang du serveur intercepté !).")
            return None
        except requests.exceptions.RequestException as e:
            self.log(f"   ↳ ❌ Erreur réseau/API : Fichier inaccessible.")
            return None
        except Exception as e:
            self.log(f"   ↳ ❌ Erreur inattendue : {str(e)}")
            return None 

        if not all_records:
            return None

        # --- TRANSFORMATION ET FILTRAGE LOCAL INTELLIGENT ---
        try:
            df = pd.DataFrame(all_records)

            cols_to_check = [col for col in df.columns if col != '_id']
            df = df.dropna(subset=cols_to_check, how='all')

            selected_govs = [var.get() for var in self.gov_vars.values() if var.get()]
            if selected_govs:
                pattern = '|'.join(selected_govs)
                mask_gov = df.apply(lambda row: row.astype(str).str.contains(pattern, case=False, na=False).any(), axis=1)
                filtered_df = df[mask_gov]
                if not filtered_df.empty:
                    df = filtered_df

            y_start = self.entry_year_start.get().strip()
            y_end = self.entry_year_end.get().strip()
            if y_start or y_end:
                years_to_search = []
                if y_start and y_end and y_start.isdigit() and y_end.isdigit():
                    years_to_search = [str(y) for y in range(int(y_start), int(y_end) + 1)]
                elif y_start:
                    years_to_search = [y_start]
                
                if years_to_search:
                    years_in_cols = any(y in df.columns for y in years_to_search)
                    if not years_in_cols:
                        pattern_years = '|'.join(years_to_search)
                        mask_year = df.apply(lambda row: row.astype(str).str.contains(pattern_years, na=False).any(), axis=1)
                        filtered_df = df[mask_year]
                        if not filtered_df.empty:
                            df = filtered_df

            return df
        except Exception as e:
            self.log(f"   ↳ ❌ Erreur lors du nettoyage avec Pandas : {str(e)}")
            return None
            
    def _save_file_dialog(self, df):
        """Dialogue de sauvegarde pour l'extraction individuelle."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Fichier CSV", "*.csv"), ("Fichier Excel", "*.xlsx")],
            title="Enregistrer la base de données OSINT"
        )
        if filepath:
            try:
                self.log("💾 Sauvegarde individuelle en cours...")
                if filepath.endswith('.csv'):
                    df.to_csv(filepath, index=False, encoding='utf-8-sig')
                else:
                    df.to_excel(filepath, index=False)
                self.log(f"✅ Extraction réussie !\nFichier : {filepath}")
            except Exception as e:
                self.log(f"❌ Erreur d'écriture sur le disque : {str(e)}")

if __name__ == "__main__":
    app = AgridataProApp()
    app.mainloop()