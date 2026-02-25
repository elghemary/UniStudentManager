
# - l'interface graphique Tkinter (GUI)


import os # biblio OS pour gestion fichiers/systèmes
import tkinter as tk
from tkinter import ttk, messagebox, filedialog # biblio Tkinter pour GUI, ttkinter.ttk pour widgets styles, messagebox pour boîtes dialogues, filedialog pour dialogues fichiers
import sqlite3 # biblio SQLite pour BD locale

from models import Repository, Student, Examen, Projet, Grade


class UniStudentManager(tk.Tk):
    # Cette classe représente la fenêtre principale.


    def __init__(self):
        super().__init__() # Initialise la fenêtre Tkinter

        # Titre + taille de fenêtre
        self.title("UniStudent Manager - Gestion Étudiants")
        self.geometry("1100x650")

        # Repository = couche d'accès BD
        self.repo = Repository("university.db")

        # Construction de l'UI
        self._build_header()
        self._build_tabs()

        # Au démarrage, on charge les données et on remplit les tableaux
        self.refresh_students()
        self.refresh_evaluations()
        self.refresh_grades()
        self.refresh_stats()


    # HEADER : logo + titre + boutons JSON
    def _build_header(self):
        # Frame = conteneur
        header = ttk.Frame(self, padding=10)
        header.pack(fill="x")  # fill="x" = occupe toute la largeur

        self.logo_img = None
        logo_path = os.path.join("assets", "logo.png")

        if os.path.exists(logo_path):
            try:
                # PhotoImage = support simple pour PNG dans Tkinter
                self.logo_img = tk.PhotoImage(file=logo_path)
                ttk.Label(header, image=self.logo_img).pack(side="left", padx=(0, 15))
            except:
                # Si erreur de chargement image, on ignore
                pass

        # Titre principal
        title = ttk.Label(
            header,
            text="UniStudent Manager\nGestion Étudiants • Examens • Projets • Notes\npar EL GHEMARY Farah • MID",
            font=("Segoe UI", 16, "bold")
        )
        title.pack(side="left")

        # Petits boutons à droite pour sauvegarder/charger la base en JSON
        ttk.Button(header, text="Sauvegarder JSON", command=self.export_json).pack(side="right", padx=5)
        ttk.Button(header, text="Charger JSON", command=self.import_json).pack(side="right", padx=5)

    # NOTEBOOK = onglets
    def _build_tabs(self):
        # Notebook = widget d'onglets
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Un Frame par onglet
        self.tab_students = ttk.Frame(self.notebook)
        self.tab_evals = ttk.Frame(self.notebook)
        self.tab_grades = ttk.Frame(self.notebook)
        self.tab_stats = ttk.Frame(self.notebook)

        # Ajout des onglets
        self.notebook.add(self.tab_students, text="Étudiants")
        self.notebook.add(self.tab_evals, text="Évaluations")
        self.notebook.add(self.tab_grades, text="Notes")
        self.notebook.add(self.tab_stats, text="Statistiques")

        # Construction UI de chaque onglet
        self._students_ui()
        self._evals_ui()
        self._grades_ui()
        self._stats_ui()

    # JSON
    def export_json(self):
        # Dialog pour choisir où enregistrer le fichier
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")]
        )
        if not filepath:
            return

        try:
            self.repo.export_json(filepath)
            messagebox.showinfo("OK", "Sauvegarde JSON réussie.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def import_json(self):
        # Dialog pour choisir un fichier JSON à charger
        filepath = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not filepath:
            return

        try:
            self.repo.import_json(filepath)
            # Après import, on rafraîchit tous les tableaux
            self.refresh_students()
            self.refresh_evaluations()
            self.refresh_grades()
            self.refresh_stats()
            messagebox.showinfo("OK", "Chargement JSON réussi.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    # ONGLET 1 : ETUDIANTS 

    def _students_ui(self):
        # Variables Tkinter :
        # StringVar permet de lier une entrée  à une variable Python.
        self.s_cne = tk.StringVar()
        self.s_nom = tk.StringVar()
        self.s_prenom = tk.StringVar()
        self.s_groupe = tk.StringVar()
        self.s_filiere = tk.StringVar()
        self.s_email = tk.StringVar()
        self.s_search = tk.StringVar()

        # FORMULAIRE
        top = ttk.Frame(self.tab_students, padding=10)
        top.pack(fill="x")

        fields_row0 = [
            ("CNE*", self.s_cne),
            ("Nom*", self.s_nom),
            ("Prénom*", self.s_prenom),
            ("Groupe*", self.s_groupe),
            ("Filière*", self.s_filiere),
        ]

        # Ligne 0 : 5 champs (label + entry)
        for i, (label, var) in enumerate(fields_row0): 
            # 2 colonnes par champ : label puis entry
            ttk.Label(top, text=label).grid(row=0, column=2*i, sticky="w", padx=5, pady=5) 
            ttk.Entry(top, textvariable=var, width=20).grid(row=0, column=2*i+1, sticky="w", padx=5, pady=5)

        # Ligne 1 : Email sur plusieurs colonnes, plus large
        ttk.Label(top, text="Email").grid(row=1, column=0, sticky="w", padx=5, pady=5)

        ttk.Entry(top, textvariable=self.s_email, width=70).grid(
            row=1, column=1, columnspan=9, sticky="w", padx=5, pady=5
        )

        # BOUTONS
        btns = ttk.Frame(self.tab_students, padding=10)
        btns.pack(fill="x")

        ttk.Button(btns, text="Ajouter", command=self.add_student).pack(side="left", padx=5)
        ttk.Button(btns, text="Modifier (sélection)", command=self.update_student).pack(side="left", padx=5)
        ttk.Button(btns, text="Supprimer (sélection)", command=self.delete_student).pack(side="left", padx=5)

        # BARRE DE RECHERCHE 
        searchbar = ttk.Frame(self.tab_students, padding=10)
        searchbar.pack(fill="x")

        ttk.Label(searchbar, text="Recherche (nom / CNE / groupe) :").pack(side="left")
        ttk.Entry(searchbar, textvariable=self.s_search, width=40).pack(side="left", padx=8)
        ttk.Button(searchbar, text="Rechercher", command=self.refresh_students).pack(side="left")
        ttk.Button(searchbar, text="Reset", command=self.reset_student_search).pack(side="left", padx=5)

        # TABLEAU
        # Treeview = tableau avec colonnes.
        self.students_tree = ttk.Treeview(
            self.tab_students,
            columns=("id", "cne", "nom", "prenom", "groupe", "filiere", "email"),
            show="headings",
            height=18
        )

        # Définition des en-têtes et largeur de colonnes
        columns = [
            ("id", 60),
            ("cne", 120),
            ("nom", 140),
            ("prenom", 140),
            ("groupe", 100),
            ("filiere", 140),
            ("email", 220),
        ]

        for col, w in columns:
            self.students_tree.heading(col, text=col.upper())
            self.students_tree.column(col, width=w, anchor="w")

        self.students_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Quand l'utilisateur clique une ligne du tableau,
        # on copie ses données dans les champs (pour modifier facilement).
        self.students_tree.bind("<<TreeviewSelect>>", self.on_student_select)

    def reset_student_search(self):
        self.s_search.set("")
        self.refresh_students()

    def on_student_select(self, _event=None):
        item = self.students_tree.selection()
        if not item:
            return

        values = self.students_tree.item(item[0], "values")
        # values = (id, cne, nom, prenom, groupe, filiere, email)

        self.s_cne.set(values[1])
        self.s_nom.set(values[2])
        self.s_prenom.set(values[3])
        self.s_groupe.set(values[4])
        self.s_filiere.set(values[5])
        self.s_email.set(values[6])

    def refresh_students(self):
        # Efface tout le contenu du tableau
        for row in self.students_tree.get_children():
            self.students_tree.delete(row)

        # Récupère les données depuis la base (avec recherche si query)
        rows = self.repo.list_students(self.s_search.get())

        # Insère chaque ligne dans le Treeview
        for r in rows:
            self.students_tree.insert("", "end", values=r)

        # On rafraîchit aussi les stats (car elles dépendent des étudiants/notes)
        self.refresh_stats()

    def add_student(self):
        try:
            # Créer un objet Student déclenche les validations (setters)
            s = Student(
                self.s_cne.get(),
                self.s_nom.get(),
                self.s_prenom.get(),
                self.s_groupe.get(),
                self.s_filiere.get(),
                self.s_email.get()
            )

            # Insérer dans la base via repo
            self.repo.add_student(s)

            # Refresh UI
            self.refresh_students()
            messagebox.showinfo("OK", "Étudiant ajouté.")

        except sqlite3.IntegrityError:
            # Erreur SQLite : CNE UNIQUE déjà existant
            messagebox.showerror("Erreur", "CNE déjà existant (doit être unique).")
        except Exception as e:
            # Erreurs de validation (ValueError) ou autres
            messagebox.showerror("Erreur", str(e))

    def update_student(self):
        item = self.students_tree.selection()
        if not item:
            messagebox.showwarning("Sélection", "Sélectionnez un étudiant à modifier.")
            return

        student_id = int(self.students_tree.item(item[0], "values")[0])

        try:
            s = Student(
                self.s_cne.get(),
                self.s_nom.get(),
                self.s_prenom.get(),
                self.s_groupe.get(),
                self.s_filiere.get(),
                self.s_email.get()
            )

            self.repo.update_student(student_id, s)
            self.refresh_students()
            messagebox.showinfo("OK", "Étudiant modifié.")

        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "CNE déjà existant (unique).")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def delete_student(self):
        item = self.students_tree.selection()
        if not item:
            messagebox.showwarning("Sélection", "Sélectionnez un étudiant à supprimer.")
            return

        student_id = int(self.students_tree.item(item[0], "values")[0])

        if not messagebox.askyesno("Confirmation", "Supprimer cet étudiant ? (notes incluses)"):
            return

        try:
            self.repo.delete_student(student_id)
            self.refresh_students()
            self.refresh_grades()  # car notes dépend des étudiants
            messagebox.showinfo("OK", "Étudiant supprimé.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    # ONGLET 2 : EVALUATIONS

    def _evals_ui(self):
        top = ttk.Frame(self.tab_evals, padding=10)
        top.pack(fill="x")

        self.e_type = tk.StringVar(value="Examen")
        self.e_titre = tk.StringVar()
        self.e_date = tk.StringVar()
        self.e_coef = tk.StringVar(value="1.0")
        self.e_note_max = tk.StringVar(value="20")

        ttk.Label(top, text="Type").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Combobox(top, textvariable=self.e_type, values=["Examen", "Projet"],
                     width=12, state="readonly").grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(top, text="Titre*").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Entry(top, textvariable=self.e_titre, width=25).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(top, text="Date (YYYY-MM-DD)").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        ttk.Entry(top, textvariable=self.e_date, width=16).grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(top, text="Coef").grid(row=0, column=6, padx=5, pady=5, sticky="w")
        ttk.Entry(top, textvariable=self.e_coef, width=8).grid(row=0, column=7, padx=5, pady=5)

        ttk.Label(top, text="Note max").grid(row=0, column=8, padx=5, pady=5, sticky="w")
        ttk.Entry(top, textvariable=self.e_note_max, width=8).grid(row=0, column=9, padx=5, pady=5)

        btns = ttk.Frame(self.tab_evals, padding=10)
        btns.pack(fill="x")
        ttk.Button(btns, text="Ajouter", command=self.add_evaluation).pack(side="left", padx=5)
        ttk.Button(btns, text="Supprimer (sélection)", command=self.delete_evaluation).pack(side="left", padx=5)

        self.evals_tree = ttk.Treeview(
            self.tab_evals,
            columns=("id", "type", "titre", "date", "coefficient", "note_max"),
            show="headings",
            height=18
        )

        columns = [
            ("id", 60),
            ("type", 90),
            ("titre", 260),
            ("date", 120),
            ("coefficient", 100),
            ("note_max", 100)
        ]

        for col, w in columns:
            self.evals_tree.heading(col, text=col.upper())
            self.evals_tree.column(col, width=w, anchor="w")

        self.evals_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_evaluations(self):
        for row in self.evals_tree.get_children():
            self.evals_tree.delete(row)

        rows = self.repo.list_evaluations()
        for r in rows:
            self.evals_tree.insert("", "end", values=r)

        self.refresh_grades()
        self.refresh_stats()

    def add_evaluation(self):
        try:
            # On instancie Examen/Projet selon le type choisi
            if self.e_type.get() == "Examen":
                e = Examen(self.e_titre.get(), self.e_date.get(), self.e_coef.get(), self.e_note_max.get())
            else:
                e = Projet(self.e_titre.get(), self.e_date.get(), self.e_coef.get(), self.e_note_max.get())

            self.repo.add_evaluation(e)
            self.refresh_evaluations()
            messagebox.showinfo("OK", "Évaluation ajoutée.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def delete_evaluation(self):
        item = self.evals_tree.selection()
        if not item:
            messagebox.showwarning("Sélection", "Sélectionnez une évaluation à supprimer.")
            return

        evaluation_id = int(self.evals_tree.item(item[0], "values")[0])

        if not messagebox.askyesno("Confirmation", "Supprimer cette évaluation ? (notes incluses)"):
            return

        try:
            self.repo.delete_evaluation(evaluation_id)
            self.refresh_evaluations()
            messagebox.showinfo("OK", "Évaluation supprimée.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    # ONGLET 3 : NOTES

    def _grades_ui(self):
        top = ttk.Frame(self.tab_grades, padding=10)
        top.pack(fill="x")

        self.g_student = tk.StringVar()
        self.g_eval = tk.StringVar()
        self.g_note = tk.StringVar()

        ttk.Label(top, text="Étudiant").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_students = ttk.Combobox(top, textvariable=self.g_student, width=35, state="readonly")
        self.combo_students.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(top, text="Évaluation").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.combo_evals = ttk.Combobox(top, textvariable=self.g_eval, width=35, state="readonly")
        self.combo_evals.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(top, text="Note").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        ttk.Entry(top, textvariable=self.g_note, width=10).grid(row=0, column=5, padx=5, pady=5)

        btns = ttk.Frame(self.tab_grades, padding=10)
        btns.pack(fill="x")
        ttk.Button(btns, text="Enregistrer / Mettre à jour", command=self.save_grade).pack(side="left", padx=5)
        ttk.Button(btns, text="Supprimer (sélection)", command=self.delete_grade).pack(side="left", padx=5)

        self.grades_tree = ttk.Treeview(
            self.tab_grades,
            columns=("grade_id", "cne", "nom", "prenom", "evaluation", "type", "note"),
            show="headings",
            height=18
        )

        columns = [
            ("grade_id", 80),
            ("cne", 120),
            ("nom", 140),
            ("prenom", 140),
            ("evaluation", 260),
            ("type", 90),
            ("note", 80),
        ]
        for col, w in columns:
            self.grades_tree.heading(col, text=col.upper())
            self.grades_tree.column(col, width=w, anchor="w")

        self.grades_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_grades(self):
        # Remplir Combobox étudiants
        students = self.repo.list_students_for_combo()
        self.students_map = {}  # map label -> id
        labels_students = []
        for sid, cne, nom, prenom in students:
            label = f"{cne} - {nom} {prenom}"
            self.students_map[label] = sid
            labels_students.append(label)
        self.combo_students["values"] = labels_students

        # Remplir Combobox évaluations
        evals = self.repo.list_evals_for_combo()
        self.evals_map = {}  # map label -> id
        labels_evals = []
        for eid, typ, titre in evals:
            label = f"{typ} - {titre}"
            self.evals_map[label] = eid
            labels_evals.append(label)
        self.combo_evals["values"] = labels_evals

        # Remplir tableau des notes
        for row in self.grades_tree.get_children():
            self.grades_tree.delete(row)

        rows = self.repo.list_grades()
        for r in rows:
            self.grades_tree.insert("", "end", values=r)

        self.refresh_stats()

    def save_grade(self):
        # Vérifier choix
        student_label = self.g_student.get()
        eval_label = self.g_eval.get()
        if student_label not in self.students_map or eval_label not in self.evals_map:
            messagebox.showwarning("Champs", "Choisissez un étudiant et une évaluation.")
            return

        try:
            # Grade valide note (0..20)
            g = Grade(self.g_note.get())

            sid = self.students_map[student_label]
            eid = self.evals_map[eval_label]

            self.repo.upsert_grade(sid, eid, g)
            self.refresh_grades()
            messagebox.showinfo("OK", "Note enregistrée / mise à jour.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def delete_grade(self):
        item = self.grades_tree.selection()
        if not item:
            messagebox.showwarning("Sélection", "Sélectionnez une note à supprimer.")
            return

        grade_id = int(self.grades_tree.item(item[0], "values")[0])

        if not messagebox.askyesno("Confirmation", "Supprimer cette note ?"):
            return

        try:
            self.repo.delete_grade(grade_id)
            self.refresh_grades()
            messagebox.showinfo("OK", "Note supprimée.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    # ONGLET 4 : STATISTIQUES
    def _stats_ui(self):
        frame = ttk.Frame(self.tab_stats, padding=15)
        frame.pack(fill="both", expand=True)

        # Text = zone multi-lignes pour afficher du texte
        self.stats_text = tk.Text(frame, height=25, wrap="word")
        self.stats_text.pack(fill="both", expand=True)

        ttk.Button(frame, text="Rafraîchir", command=self.refresh_stats).pack(pady=10)

    def refresh_stats(self):
        # On récupère tous les étudiants
        students = self.repo.list_students()

        # avgs = liste (nom, prenom, moyenne)
        avgs = []

        for (sid, cne, nom, prenom, groupe, filiere, email) in students:
            avg = self.repo.student_average(int(sid))
            if avg is not None:
                avgs.append((nom, prenom, avg))

        class_avg = (sum(a[2] for a in avgs) / len(avgs)) if avgs else None
        success = [a for a in avgs if a[2] >= 10]
        risk = [a for a in avgs if a[2] < 10]
        top5 = sorted(avgs, key=lambda x: x[2], reverse=True)[:5]

        # Nettoyage de l'affichage
        self.stats_text.delete("1.0", tk.END)

        self.stats_text.insert(tk.END, "=== DASHBOARD ===\n")
        self.stats_text.insert(tk.END, f"Nombre d'étudiants : {len(students)}\n")
        self.stats_text.insert(tk.END, f"Étudiants avec notes : {len(avgs)}\n")

        if class_avg is not None:
            self.stats_text.insert(tk.END, f"Moyenne de classe (pondérée) : {class_avg:.2f}/20\n")
            taux = (len(success) / len(avgs)) * 100 if avgs else 0
            self.stats_text.insert(tk.END, f"Taux de réussite (>=10) : {taux:.1f}%\n")
        else:
            self.stats_text.insert(tk.END, "Moyenne de classe : N/A (aucune note)\n")

        self.stats_text.insert(tk.END, "\n=== TOP 5 ===\n")
        if top5:
            for nom, prenom, avg in top5:
                badge = "Excellent" if avg >= 16 else "Très bien" if avg >= 14 else ""
                extra = f" ({badge})" if badge else ""
                self.stats_text.insert(tk.END, f"- {nom} {prenom} : {avg:.2f}/20{extra}\n")
        else:
            self.stats_text.insert(tk.END, "Aucun résultat.\n")

        self.stats_text.insert(tk.END, "\n=== À RISQUE (<10) ===\n")
        if risk:
            for nom, prenom, avg in sorted(risk, key=lambda x: x[2]):
                self.stats_text.insert(tk.END, f"- {nom} {prenom} : {avg:.2f}/20 (À suivre)\n")
        else:
            self.stats_text.insert(tk.END, "Aucun étudiant à risque.\n")


if __name__ == "__main__":
    app = UniStudentManager()
    app.mainloop()
