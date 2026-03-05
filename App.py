import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from models import Database, Student, Evaluation, Grade

class UniStudentManager(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("UniStudent Manager")

        self.geometry("1100x650")

        self.db = Database("university.db")

        self.build_header() 
        self.build_tabs()

        self.refresh_students()
        self.refresh_evaluations()
        self.refresh_grades()
        self.refresh_stats()

    def build_header(self):

        header = ttk.Frame(self, padding=10)

        header.pack(fill="x")

        titre_label = ttk.Label(
            header,
            text="UniStudent Manager\nGestion Étudiants • Examens • Projets • Notes",
            font=("Segoe UI", 16, "bold") 
        )
        titre_label.pack(side="left")

        btn_save = ttk.Button(header, text="Sauvegarder JSON", command=self.export_json)
        btn_save.pack(side="right", padx=5)
        btn_load = ttk.Button(header, text="Charger JSON", command=self.import_json)
        btn_load.pack(side="right", padx=5)

    def build_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_students = ttk.Frame(self.notebook)
        self.tab_evals    = ttk.Frame(self.notebook)
        self.tab_grades   = ttk.Frame(self.notebook)
        self.tab_stats    = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_students, text="Étudiants")
        self.notebook.add(self.tab_evals,    text="Évaluations")
        self.notebook.add(self.tab_grades,   text="Notes")
        self.notebook.add(self.tab_stats,    text="Statistiques")

        self.build_students_tab()
        self.build_evals_tab()
        self.build_grades_tab()
        self.build_stats_tab()

    def build_students_tab(self):
        self.var_cne     = tk.StringVar()
        self.var_nom     = tk.StringVar()
        self.var_prenom  = tk.StringVar()
        self.var_groupe  = tk.StringVar()
        self.var_filiere = tk.StringVar()
        self.var_email   = tk.StringVar()
        self.var_search  = tk.StringVar()

        form_frame = ttk.Frame(self.tab_students, padding=10)
        form_frame.pack(fill="x")


        ttk.Label(form_frame, text="CNE*").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.var_cne, width=18).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Nom*").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.var_nom, width=18).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Prénom*").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.var_prenom, width=18).grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(form_frame, text="Groupe*").grid(row=0, column=6, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.var_groupe, width=10).grid(row=0, column=7, padx=5, pady=5)

        ttk.Label(form_frame, text="Filière*").grid(row=0, column=8, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.var_filiere, width=10).grid(row=0, column=9, padx=5, pady=5)

        ttk.Label(form_frame, text="Email").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.var_email, width=60).grid(
            row=1, column=1, columnspan=9, sticky="w", padx=5, pady=5)

        btn_frame = ttk.Frame(self.tab_students, padding=10)
        btn_frame.pack(fill="x")

        ttk.Button(btn_frame, text="Ajouter",            command=self.add_student).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Modifier (sélection)", command=self.update_student).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Supprimer (sélection)", command=self.delete_student).pack(side="left", padx=5)

        search_frame = ttk.Frame(self.tab_students, padding=10)
        search_frame.pack(fill="x")

        ttk.Label(search_frame, text="Recherche :").pack(side="left")
        ttk.Entry(search_frame, textvariable=self.var_search, width=35).pack(side="left", padx=8)
        ttk.Button(search_frame, text="Rechercher", command=self.refresh_students).pack(side="left")
        ttk.Button(search_frame, text="Effacer",    command=self.clear_search).pack(side="left", padx=5)

        self.tree_students = ttk.Treeview(
            self.tab_students,
            columns=("id", "cne", "nom", "prenom", "groupe", "filiere", "email"),
            show="headings", 
            height=18
        )

        self.tree_students.heading("id",      text="ID")
        self.tree_students.heading("cne",     text="CNE")
        self.tree_students.heading("nom",     text="NOM")
        self.tree_students.heading("prenom",  text="PRÉNOM")
        self.tree_students.heading("groupe",  text="GROUPE")
        self.tree_students.heading("filiere", text="FILIÈRE")
        self.tree_students.heading("email",   text="EMAIL")

        self.tree_students.column("id",      width=50)
        self.tree_students.column("cne",     width=120)
        self.tree_students.column("nom",     width=140)
        self.tree_students.column("prenom",  width=140)
        self.tree_students.column("groupe",  width=90)
        self.tree_students.column("filiere", width=100)
        self.tree_students.column("email",   width=220)

        self.tree_students.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree_students.bind("<<TreeviewSelect>>", self.on_student_click)

    def on_student_click(self, event=None):
        selected = self.tree_students.selection()

        if not selected:
            return
        values = self.tree_students.item(selected[0], "values")

        self.selected_student_id = int(values[0])

        self.var_cne.set(values[1]) 
        self.var_nom.set(values[2])
        self.var_prenom.set(values[3])
        self.var_groupe.set(values[4])
        self.var_filiere.set(values[5])
        self.var_email.set(values[6])

    def clear_search(self):
        self.var_search.set("") 
        self.refresh_students()

    def refresh_students(self):
        for row in self.tree_students.get_children():
            self.tree_students.delete(row)

        search_text = self.var_search.get() 
        students = self.db.get_all_students(search_text)

        for student in students:
            self.tree_students.insert("", "end", values=student)

    def add_student(self):
        try:
            student = Student(
                cne     = self.var_cne.get(),
                nom     = self.var_nom.get(),
                prenom  = self.var_prenom.get(),
                groupe  = self.var_groupe.get(),
                filiere = self.var_filiere.get(),
                email   = self.var_email.get()
            )
            self.db.add_student(student)
            self.refresh_students()
            messagebox.showinfo("Succès", "Étudiant ajouté avec succès !")

        except Exception as erreur:
            messagebox.showerror("Erreur", str(erreur))

    def update_student(self):
        if not hasattr(self, "selected_student_id"):
            messagebox.showwarning("Attention", "Sélectionnez d'abord un étudiant dans le tableau.")
            return

        try:
            student = Student(
                cne     = self.var_cne.get(),
                nom     = self.var_nom.get(),
                prenom  = self.var_prenom.get(),
                groupe  = self.var_groupe.get(),
                filiere = self.var_filiere.get(),
                email   = self.var_email.get()
            )

            self.db.update_student(self.selected_student_id, student)
            self.refresh_students()
            messagebox.showinfo("Succès", "Étudiant modifié avec succès !")

        except Exception as erreur:
            messagebox.showerror("Erreur", str(erreur))

    def delete_student(self):
        selected = self.tree_students.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez d'abord un étudiant.")
            return

        confirm = messagebox.askyesno("Confirmation", "Supprimer cet étudiant ?")
        if not confirm:
            return

        values = self.tree_students.item(selected[0], "values")
        student_id = int(values[0]) 

        try:
            self.db.delete_student(student_id)
            self.refresh_students()
            messagebox.showinfo("Succès", "Étudiant supprimé.")

        except Exception as erreur:
            messagebox.showerror("Erreur", str(erreur))

    def build_evals_tab(self):

        self.var_type_eval  = tk.StringVar(value="Examen") 
        self.var_titre_eval = tk.StringVar()
        self.var_date_eval  = tk.StringVar()
        self.var_coef_eval  = tk.StringVar(value="1.0")
        self.var_nmax_eval  = tk.StringVar(value="20.0")

        form_frame = ttk.Frame(self.tab_evals, padding=10)
        form_frame.pack(fill="x")

        ttk.Label(form_frame, text="Type").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        combo_type = ttk.Combobox(form_frame, textvariable=self.var_type_eval,
                                  values=["Examen", "Projet"], width=12, state="readonly")
        combo_type.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Titre*").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.var_titre_eval, width=25).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Date (AAAA-MM-JJ)").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.var_date_eval, width=15).grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(form_frame, text="Coefficient").grid(row=0, column=6, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.var_coef_eval, width=8).grid(row=0, column=7, padx=5, pady=5)

        ttk.Label(form_frame, text="Note max").grid(row=0, column=8, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.var_nmax_eval, width=8).grid(row=0, column=9, padx=5, pady=5)

        btn_frame = ttk.Frame(self.tab_evals, padding=10)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Ajouter",             command=self.add_evaluation).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Supprimer (sélection)", command=self.delete_evaluation).pack(side="left", padx=5)

        self.tree_evals = ttk.Treeview(
            self.tab_evals,
            columns=("id", "type_eval", "titre", "date", "coefficient", "note_max"),
            show="headings",
            height=20
        )

        self.tree_evals.heading("id",          text="ID")
        self.tree_evals.heading("type_eval",   text="TYPE")
        self.tree_evals.heading("titre",       text="TITRE")
        self.tree_evals.heading("date",        text="DATE")
        self.tree_evals.heading("coefficient", text="COEFFICIENT")
        self.tree_evals.heading("note_max",    text="NOTE MAX")

        self.tree_evals.column("id",          width=50)
        self.tree_evals.column("type_eval",   width=100)
        self.tree_evals.column("titre",       width=220)
        self.tree_evals.column("date",        width=120)
        self.tree_evals.column("coefficient", width=120)
        self.tree_evals.column("note_max",    width=120)

        self.tree_evals.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_evaluations(self):
        for row in self.tree_evals.get_children():
            self.tree_evals.delete(row)

        evaluations = self.db.get_all_evaluations()
        for eval_row in evaluations:
            self.tree_evals.insert("", "end", values=eval_row)

    def add_evaluation(self):
        try:
            evaluation = Evaluation(
                type_eval   = self.var_type_eval.get(),
                titre       = self.var_titre_eval.get(),
                date        = self.var_date_eval.get(),
                coefficient = self.var_coef_eval.get(),
                note_max    = self.var_nmax_eval.get()
            )

            self.db.add_evaluation(evaluation)
            self.refresh_evaluations()
            messagebox.showinfo("Succès", "Évaluation ajoutée !")

        except Exception as erreur:
            messagebox.showerror("Erreur", str(erreur))

    def delete_evaluation(self):
        selected = self.tree_evals.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez une évaluation.")
            return

        confirm = messagebox.askyesno("Confirmation", "Supprimer cette évaluation ? (les notes associées seront aussi supprimées)")
        if not confirm:
            return

        values = self.tree_evals.item(selected[0], "values")
        evaluation_id = int(values[0])

        try:
            self.db.delete_evaluation(evaluation_id)
            self.refresh_evaluations()
            messagebox.showinfo("Succès", "Évaluation supprimée.")

        except Exception as erreur:
            messagebox.showerror("Erreur", str(erreur))

    def build_grades_tab(self):

        self.var_grade_student = tk.StringVar()
        self.var_grade_eval    = tk.StringVar()
        self.var_grade_note    = tk.StringVar()

        form_frame = ttk.Frame(self.tab_grades, padding=10)
        form_frame.pack(fill="x")

        ttk.Label(form_frame, text="Étudiant").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_grade_student = ttk.Combobox(form_frame, textvariable=self.var_grade_student,
                                                width=38, state="readonly")
        self.combo_grade_student.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Évaluation").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.combo_grade_eval = ttk.Combobox(form_frame, textvariable=self.var_grade_eval,
                                             width=38, state="readonly")
        self.combo_grade_eval.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Note (/20)").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        ttk.Entry(form_frame, textvariable=self.var_grade_note, width=10).grid(row=0, column=5, padx=5, pady=5)

        btn_frame = ttk.Frame(self.tab_grades, padding=10)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Enregistrer / Modifier", command=self.save_grade).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Supprimer (sélection)",  command=self.delete_grade).pack(side="left", padx=5)

        self.tree_grades = ttk.Treeview(
            self.tab_grades,
            columns=("id", "cne", "nom", "prenom", "evaluation", "type_eval", "note"),
            show="headings",
            height=18
        )

        self.tree_grades.heading("id",         text="ID")
        self.tree_grades.heading("cne",        text="CNE")
        self.tree_grades.heading("nom",        text="NOM")
        self.tree_grades.heading("prenom",     text="PRÉNOM")
        self.tree_grades.heading("evaluation", text="ÉVALUATION")
        self.tree_grades.heading("type_eval",  text="TYPE")
        self.tree_grades.heading("note",       text="NOTE")

        self.tree_grades.column("id",         width=50)
        self.tree_grades.column("cne",        width=120)
        self.tree_grades.column("nom",        width=140)
        self.tree_grades.column("prenom",     width=140)
        self.tree_grades.column("evaluation", width=250)
        self.tree_grades.column("type_eval",  width=90)
        self.tree_grades.column("note",       width=70)

        self.tree_grades.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_grades(self):
        self.student_id_map = {}  
        student_labels = []

        for row in self.db.get_students_for_dropdown():
            label = row[1] + " - " + row[2] + " " + row[3] 
            self.student_id_map[label] = row[0]              
            student_labels.append(label)

        self.combo_grade_student["values"] = student_labels 
        self.eval_id_map = {} 
        eval_labels = []

        for row in self.db.get_evaluations_for_dropdown():
            label = row[1] + " - " + row[2]
            self.eval_id_map[label] = row[0]
            eval_labels.append(label)

        self.combo_grade_eval["values"] = eval_labels

        for row in self.tree_grades.get_children():
            self.tree_grades.delete(row)

        for grade_row in self.db.get_all_grades():
            self.tree_grades.insert("", "end", values=grade_row)

        self.refresh_stats()

    def save_grade(self):
        student_label = self.var_grade_student.get()
        eval_label    = self.var_grade_eval.get()

        if student_label not in self.student_id_map or eval_label not in self.eval_id_map:
            messagebox.showwarning("Attention", "Sélectionnez un étudiant et une évaluation.")
            return

        try:
            grade = Grade(self.var_grade_note.get()) 

            student_id    = self.student_id_map[student_label]
            evaluation_id = self.eval_id_map[eval_label]

            self.db.save_grade(student_id, evaluation_id, grade)
            self.refresh_grades()
            messagebox.showinfo("Succès", "Note enregistrée !")

        except Exception as erreur:
            messagebox.showerror("Erreur", str(erreur))

    def delete_grade(self):
        selected = self.tree_grades.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez une note.")
            return

        confirm = messagebox.askyesno("Confirmation", "Supprimer cette note ?")
        if not confirm:
            return

        values  = self.tree_grades.item(selected[0], "values")
        grade_id = int(values[0])

        try:
            self.db.delete_grade(grade_id)
            self.refresh_grades()
            messagebox.showinfo("Succès", "Note supprimée.")

        except Exception as erreur:
            messagebox.showerror("Erreur", str(erreur))

    def build_stats_tab(self):
        frame = ttk.Frame(self.tab_stats, padding=15)
        frame.pack(fill="both", expand=True)

        self.stats_text = tk.Text(frame, height=28, wrap="word")
        self.stats_text.pack(fill="both", expand=True)

        ttk.Button(frame, text="Rafraîchir", command=self.refresh_stats).pack(pady=10)

    def refresh_stats(self):
        all_students = self.db.get_all_students()

        averages = []

        for student in all_students:
            student_id = int(student[0])
            nom        = student[2]
            prenom     = student[3]

            moyenne = self.db.get_student_average(student_id)

            if moyenne is not None:
                averages.append((nom, prenom, moyenne))

        self.stats_text.delete("1.0", tk.END)

        self.stats_text.insert(tk.END, "=== TABLEAU DE BORD ===\n\n")
        self.stats_text.insert(tk.END, "Nombre total d'étudiants : " + str(len(all_students)) + "\n")
        self.stats_text.insert(tk.END, "Étudiants avec au moins une note : " + str(len(averages)) + "\n\n")

        if len(averages) > 0:
            somme_moyennes = 0
            for nom, prenom, moy in averages:
                somme_moyennes = somme_moyennes + moy   

            moyenne_classe = somme_moyennes / len(averages)

            self.stats_text.insert(tk.END, "Moyenne de la classe : " + str(round(moyenne_classe, 2)) + "/20\n")
  
            recus    = []
            a_risque = []
            for nom, prenom, moy in averages:
                if moy >= 10:
                    recus.append((nom, prenom, moy))
                else:
                    a_risque.append((nom, prenom, moy))

            taux_reussite = (len(recus) / len(averages)) * 100
            self.stats_text.insert(tk.END, "Taux de réussite (>=10) : " + str(round(taux_reussite, 1)) + "%\n\n")

            top5 = sorted(averages, key=lambda x: x[2], reverse=True)[:5]

            self.stats_text.insert(tk.END, "=== TOP 5 ===\n")
            for nom, prenom, moy in top5:
                ligne = "- " + nom + " " + prenom + " : " + str(round(moy, 2)) + "/20"
                if moy >= 16:
                    ligne = ligne + " (Excellent !)"
                elif moy >= 14:
                    ligne = ligne + " (Très bien)"
                self.stats_text.insert(tk.END, ligne + "\n")

            self.stats_text.insert(tk.END, "\n=== ÉTUDIANTS À RISQUE (<10) ===\n")
            if len(a_risque) == 0:
                self.stats_text.insert(tk.END, "Aucun étudiant à risque.\n")
            else:
                for nom, prenom, moy in sorted(a_risque, key=lambda x: x[2]):
                    self.stats_text.insert(tk.END, "- " + nom + " " + prenom + " : " + str(round(moy, 2)) + "/20\n")

        else:
            self.stats_text.insert(tk.END, "Pas encore de notes enregistrées.\n")

    def export_json(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Fichier JSON", "*.json")]
        )

        if filepath == "": 
            return

        try:
            self.db.export_to_json(filepath)
            messagebox.showinfo("Succès", "Sauvegarde JSON réussie !")

        except Exception as erreur:
            messagebox.showerror("Erreur", str(erreur))

    def import_json(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Fichier JSON", "*.json")]
        )

        if filepath == "": 
            return

        try:
            self.db.import_from_json(filepath)

            self.refresh_students()
            self.refresh_evaluations()
            self.refresh_grades()
            self.refresh_stats()

            messagebox.showinfo("Succès", "Chargement JSON réussi !")

        except Exception as erreur:
            messagebox.showerror("Erreur", str(erreur))

if __name__ == "__main__":
    app = UniStudentManager()
    app.mainloop()
