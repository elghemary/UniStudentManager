import sqlite3 # SQLite database
import json
from typing import Dict, Any, Optional

class Subject:
    def __init__(self, name: str, teacher_id: int = None):
        self.name = name
        self.teacher_id = teacher_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        value = str(value).strip()
        if value == "":
            raise ValueError("Nom de matière invalide (vide).")
        self._name = value

    @property
    def teacher_id(self):
        return self._teacher_id

    @teacher_id.setter
    def teacher_id(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("L'identifiant de l'enseignant doit être un entier ou None.")
        self._teacher_id = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "teacher_id": self.teacher_id,
        }

class Teacher:
    def __init__(self, name: str, email: str = ""):
        self.name = name
        self.email = email

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        value = str(value).strip()
        if value == "":
            raise ValueError("Nom d'enseignant invalide (vide).")
        self._name = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = str(value).strip()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "email": self.email,
        }

import sqlite3 # SQLite database
import json
from typing import Dict, Any, Optional


# 1) CLASSES METIER 

class Student:
    def __init__(self, cne: str, nom: str, prenom: str, groupe: str, filiere: str, email: str = ""):
        self.cne = cne
        self.nom = nom
        self.prenom = prenom
        self.groupe = groupe
        self.filiere = filiere
        self.email = email

    @property
    def cne(self):
        return self._cne

    @cne.setter
    def cne(self, value):
        value = str(value).strip()
        if value == "":
            raise ValueError("CNE invalide (vide).")
        self._cne = value

    @property
    def nom(self):
        return self._nom

    @nom.setter
    def nom(self, value):
        value = str(value).strip()
        if value == "" or value.isdigit():
            raise ValueError("Nom invalide.")
        self._nom = value

    @property
    def prenom(self):
        return self._prenom

    @prenom.setter
    def prenom(self, value):
        value = str(value).strip()
        if value == "" or value.isdigit():
            raise ValueError("Prénom invalide.")
        self._prenom = value

    @property
    def groupe(self):
        return self._groupe

    @groupe.setter
    def groupe(self, value):
        value = str(value).strip()
        if value == "":
            raise ValueError("Groupe invalide.")
        self._groupe = value

    @property
    def filiere(self):
        return self._filiere

    @filiere.setter
    def filiere(self, value):
        value = str(value).strip()
        if value == "":
            raise ValueError("Filière invalide.")
        self._filiere = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = str(value).strip()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cne": self.cne,
            "nom": self.nom,
            "prenom": self.prenom,
            "groupe": self.groupe,
            "filiere": self.filiere,
            "email": self.email,
        }


class Evaluation:
    def __init__(self, titre: str, date: str = "", coefficient: float = 1.0, note_max: float = 20.0):
        self.titre = titre
        self.date = date
        self.coefficient = coefficient
        self.note_max = note_max

    @property
    def type(self) -> str:
        return "Evaluation"

    @property
    def titre(self):
        return self._titre

    @titre.setter
    def titre(self, value):
        value = str(value).strip()
        if value == "":
            raise ValueError("Titre invalide (vide).")
        self._titre = value

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = str(value).strip()


    @property
    def coefficient(self):
        return self._coefficient

    @coefficient.setter
    def coefficient(self, value):
        try:
            v = float(value)
        except (ValueError, TypeError):
            raise ValueError("Coefficient invalide (doit être un nombre).")
        if v <= 0:
            raise ValueError("Coefficient doit être > 0.")
        self._coefficient = v

    @property
    def note_max(self):
        return self._note_max

    @note_max.setter
    def note_max(self, value):
        try:
            v = float(value)
        except (ValueError, TypeError):
            raise ValueError("Note max invalide (doit être un nombre).")
        if v <= 0:
            raise ValueError("Note max doit être > 0.")
        self._note_max = v

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "titre": self.titre,
            "date": self.date,
            "coefficient": self.coefficient,
            "note_max": self.note_max,
        }


class Examen(Evaluation):
    @property
    def type(self) -> str:
        return "Examen"


class Projet(Evaluation):
    @property
    def type(self) -> str:
        return "Projet"


class Grade:

    def __init__(self, note: float):
        self.note = note

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, value):
        try:
            v = float(value)
        except (ValueError, TypeError):
            raise ValueError("Note invalide (doit être un nombre).")
        if v < 0 or v > 20:
            raise ValueError("La note doit être entre 0 et 20.")
        self._note = v


# 2) REPOSITORY : couche d'accès à la base SQLite


class Repository:
    # Certificate generation (simple string, can be extended for PDF)
    def generate_certificate(self, student_id: int) -> str:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT nom, prenom, filiere FROM students WHERE id=?", (student_id,))
        student = cur.fetchone()
        if not student:
            conn.close()
            raise ValueError("Étudiant introuvable.")
        nom, prenom, filiere = student
        # List subjects
        cur.execute("""
            SELECT subjects.name FROM student_subjects
            JOIN subjects ON student_subjects.subject_id = subjects.id
            WHERE student_subjects.student_id = ?
        """, (student_id,))
        subjects = [row[0] for row in cur.fetchall()]
        conn.close()
        subjects_str = ', '.join(subjects) if subjects else 'aucune matière'
        certificate = (
            f"Certificat de Réussite\n"
            f"----------------------\n"
            f"Nom: {nom}\n"
            f"Prénom: {prenom}\n"
            f"Filière: {filiere}\n"
            f"Matières suivies: {subjects_str}\n"
            f"Date: 25 février 2026\n"
            f"\nFélicitations pour la réussite de votre parcours universitaire !"
        )
        return certificate

    # Administration: Link students to subjects (many-to-many)
    def init_db(self):
        # ...existing code...
        conn = self._conn()
        cur = conn.cursor()
        # ...existing code...

        # Table d'association étudiants-matières
        cur.execute("""
        CREATE TABLE IF NOT EXISTS student_subjects(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(subject_id) REFERENCES subjects(id),
            UNIQUE(student_id, subject_id)
        )
        """)
        # ...existing code...

    def assign_subject_to_student(self, student_id: int, subject_id: int):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO student_subjects(student_id, subject_id)
            VALUES (?, ?)
        """, (student_id, subject_id))
        conn.commit()
        conn.close()

    def list_student_subjects(self, student_id: int):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT subjects.id, subjects.name, teachers.name as teacher_name
            FROM student_subjects
            JOIN subjects ON student_subjects.subject_id = subjects.id
            LEFT JOIN teachers ON subjects.teacher_id = teachers.id
            WHERE student_subjects.student_id = ?
        """, (student_id,))
        rows = cur.fetchall()
        conn.close()
        return rows

    def __init__(self, db_name="university.db"):
        self.db_name = db_name
        self.init_db()

    def _conn(self):
        # Ouvre une connexion vers le fichier SQLite
        return sqlite3.connect(self.db_name)

    def init_db(self):
        # Création des tables si elles n'existent pas.
        conn = self._conn()
        cur = conn.cursor()

        # Table enseignants
        cur.execute("""
        CREATE TABLE IF NOT EXISTS teachers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT
        )
        """)

        # Table matières
        cur.execute("""
        CREATE TABLE IF NOT EXISTS subjects(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            teacher_id INTEGER,
            FOREIGN KEY(teacher_id) REFERENCES teachers(id)
        )
        """)

        # Table étudiants
        cur.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cne TEXT UNIQUE NOT NULL,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            groupe TEXT NOT NULL,
            filiere TEXT NOT NULL,
            email TEXT
        )
        """)

        # Table évaluations
        cur.execute("""
        CREATE TABLE IF NOT EXISTS evaluations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            titre TEXT NOT NULL,
            date TEXT,
            coefficient REAL DEFAULT 1.0,
            note_max REAL DEFAULT 20.0
        )
        """)

        # Table notes
        # UNIQUE(student_id, evaluation_id) = 1 note max par étudiant/évaluation
        cur.execute("""
        CREATE TABLE IF NOT EXISTS grades(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            evaluation_id INTEGER NOT NULL,
            note REAL NOT NULL,
            UNIQUE(student_id, evaluation_id),
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(evaluation_id) REFERENCES evaluations(id)
        )
        """)

        conn.commit()
        conn.close()

    # Teachers CRUD
    def add_teacher(self, t: Teacher):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO teachers(name, email)
            VALUES (?, ?)
        """, (t.name, t.email if t.email else None))
        conn.commit()
        conn.close()

    def list_teachers(self):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, COALESCE(email, '') FROM teachers ORDER BY name")
        rows = cur.fetchall()
        conn.close()
        return rows

    # Subjects CRUD
    def add_subject(self, s: Subject):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO subjects(name, teacher_id)
            VALUES (?, ?)
        """, (s.name, s.teacher_id))
        conn.commit()
        conn.close()

    def list_subjects(self):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT subjects.id, subjects.name, teachers.name as teacher_name
            FROM subjects
            LEFT JOIN teachers ON subjects.teacher_id = teachers.id
            ORDER BY subjects.name
        """)
        rows = cur.fetchall()
        conn.close()
        return rows

    # Students CRUD

    def add_student(self, s: Student):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO students(cne, nom, prenom, groupe, filiere, email)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (s.cne, s.nom, s.prenom, s.groupe, s.filiere, s.email if s.email else None))
        conn.commit()
        conn.close()

    def update_student(self, student_id: int, s: Student):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            UPDATE students
            SET cne=?, nom=?, prenom=?, groupe=?, filiere=?, email=?
            WHERE id=?
        """, (s.cne, s.nom, s.prenom, s.groupe, s.filiere, s.email if s.email else None, student_id))
        conn.commit()
        conn.close()

    def delete_student(self, student_id: int):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM grades WHERE student_id=?", (student_id,))
        cur.execute("DELETE FROM students WHERE id=?", (student_id,))
        conn.commit()
        conn.close()

    def list_students(self, query: str = ""):
        # Renvoie une liste de tuples prêts à afficher dans Treeview.
        conn = self._conn()
        cur = conn.cursor()

        q = query.strip().lower()
        if q:
            cur.execute("""
                SELECT id, cne, nom, prenom, groupe, filiere, COALESCE(email,'')
                FROM students
                WHERE lower(cne) LIKE ?
                   OR lower(nom) LIKE ?
                   OR lower(prenom) LIKE ?
                   OR lower(groupe) LIKE ?
                ORDER BY nom, prenom
            """, (f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"))
        else:
            cur.execute("""
                SELECT id, cne, nom, prenom, groupe, filiere, COALESCE(email,'')
                FROM students
                ORDER BY nom, prenom
            """)

        rows = cur.fetchall()
        conn.close()
        return rows

    # Evaluations CRUD

    def add_evaluation(self, e: Evaluation):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO evaluations(type, titre, date, coefficient, note_max)
            VALUES (?, ?, ?, ?, ?)
        """, (e.type, e.titre, e.date if e.date else None, e.coefficient, e.note_max))
        conn.commit()
        conn.close()

    def delete_evaluation(self, evaluation_id: int):
        # Supprimer aussi les notes liées à cette évaluation
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM grades WHERE evaluation_id=?", (evaluation_id,))
        cur.execute("DELETE FROM evaluations WHERE id=?", (evaluation_id,))
        conn.commit()
        conn.close()

    def list_evaluations(self):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, type, titre, COALESCE(date,''), coefficient, note_max
            FROM evaluations
            ORDER BY id DESC
        """)
        rows = cur.fetchall()
        conn.close()
        return rows

    # Grades CRUD

    def upsert_grade(self, student_id: int, evaluation_id: int, g: Grade):
        """
        Upsert = insert si n'existe pas, sinon update.
        On utilise la contrainte UNIQUE(student_id, evaluation_id) :
        - Si INSERT échoue => la note existe déjà => UPDATE.
        """
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO grades(student_id, evaluation_id, note)
                VALUES (?, ?, ?)
            """, (student_id, evaluation_id, g.note))
        except sqlite3.IntegrityError:
            cur.execute("""
                UPDATE grades SET note=?
                WHERE student_id=? AND evaluation_id=?
            """, (g.note, student_id, evaluation_id))
        conn.commit()
        conn.close()

    def delete_grade(self, grade_id: int):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM grades WHERE id=?", (grade_id,))
        conn.commit()
        conn.close()

    def list_grades(self):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT g.id, s.cne, s.nom, s.prenom, e.titre, e.type, g.note
            FROM grades g
            JOIN students s ON s.id = g.student_id
            JOIN evaluations e ON e.id = g.evaluation_id
            ORDER BY s.nom, s.prenom
        """)
        rows = cur.fetchall()
        conn.close()
        return rows

    def list_students_for_combo(self):
        # Pour remplir la Combobox "Étudiant"
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT id, cne, nom, prenom FROM students ORDER BY nom, prenom")
        rows = cur.fetchall()
        conn.close()
        return rows

    def list_evals_for_combo(self):
        # Pour remplir la Combobox "Évaluation"
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT id, type, titre FROM evaluations ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        return rows

    # Calculs (moyenne)
    

    def student_average(self, student_id: int) -> Optional[float]:
        """
        Calcule la moyenne pondérée sur 20 d'un étudiant.

        Formule :
            moyenne = sum(note_sur20 * coef) / sum(coef)

        Si note_max != 20, on normalise vers /20.
        """
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT g.note, e.coefficient, e.note_max
            FROM grades g
            JOIN evaluations e ON e.id = g.evaluation_id
            WHERE g.student_id = ?
        """, (student_id,))
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return None

        total = 0.0
        coef_sum = 0.0

        for note, coef, note_max in rows:
            if note_max and note_max != 20:
                # Normalisation : note/(note_max) * 20
                note = (note / note_max) * 20
            total += note * coef
            coef_sum += coef

        if coef_sum == 0:
            return None

        return total / coef_sum

    # JSON (Sauvegarde / Chargement)

    def export_json(self, filepath: str):
        """
        Export complet (students, evaluations, grades) en JSON.
        Très utile pour sauvegarder / transférer la base.
        """
        data = {}

        data["students"] = []
        for (sid, cne, nom, prenom, groupe, filiere, email) in self.list_students():
            data["students"].append({
                "id": sid,
                "cne": cne,
                "nom": nom,
                "prenom": prenom,
                "groupe": groupe,
                "filiere": filiere,
                "email": email
            })

        data["evaluations"] = []
        for (eid, typ, titre, date, coef, note_max) in self.list_evaluations():
            data["evaluations"].append({
                "id": eid,
                "type": typ,
                "titre": titre,
                "date": date,
                "coefficient": coef,
                "note_max": note_max
            })

        data["grades"] = []
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT id, student_id, evaluation_id, note FROM grades")
        for gid, sid, eid, note in cur.fetchall():
            data["grades"].append({
                "id": gid,
                "student_id": sid,
                "evaluation_id": eid,
                "note": note
            })
        conn.close()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_json(self, filepath: str):
        """
        Import JSON :
        - on lit le fichier
        - stratégie simple pédagogique : on vide la base puis on recharge
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        conn = self._conn()
        cur = conn.cursor()

        # On vide (ordre important : grades dépend des deux autres)
        cur.execute("DELETE FROM grades")
        cur.execute("DELETE FROM evaluations")
        cur.execute("DELETE FROM students")
        conn.commit()

        # On recharge les tables avec leurs id
        for s in data.get("students", []):
            cur.execute("""
                INSERT INTO students(id, cne, nom, prenom, groupe, filiere, email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (s["id"], s["cne"], s["nom"], s["prenom"], s["groupe"], s["filiere"], s.get("email") or None))

        for e in data.get("evaluations", []):
            cur.execute("""
                INSERT INTO evaluations(id, type, titre, date, coefficient, note_max)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (e["id"], e["type"], e["titre"], e.get("date") or None, e["coefficient"], e["note_max"]))

        for g in data.get("grades", []):
            cur.execute("""
                INSERT INTO grades(id, student_id, evaluation_id, note)
                VALUES (?, ?, ?, ?)
            """, (g["id"], g["student_id"], g["evaluation_id"], g["note"]))

        conn.commit()
        conn.close()
