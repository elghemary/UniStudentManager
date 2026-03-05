import sqlite3
import json 

class Student:
    def __init__(self, cne, nom, prenom, groupe, filiere, email=""):
        if cne.strip() == "":
            raise ValueError("Le CNE ne peut pas être vide !")
        if nom.strip() == "":
            raise ValueError("Le nom ne peut pas être vide !")
        if prenom.strip() == "":
            raise ValueError("Le prénom ne peut pas être vide !")
        if groupe.strip() == "":
            raise ValueError("Le groupe ne peut pas être vide !")
        if filiere.strip() == "":
            raise ValueError("La filière ne peut pas être vide !")

        self.cne = cne.strip()
        self.nom = nom.strip()
        self.prenom = prenom.strip()
        self.groupe = groupe.strip()
        self.filiere = filiere.strip()
        self.email = email.strip()

class Evaluation:
    def __init__(self, type_eval, titre, date, coefficient, note_max):
        if titre.strip() == "":
            raise ValueError("Le titre ne peut pas être vide !")
        try:
            coefficient = float(coefficient)
        except:
            raise ValueError("Le coefficient doit être un nombre !")

        if coefficient <= 0:
            raise ValueError("Le coefficient doit être supérieur à 0 !")

        try:
            note_max = float(note_max)
        except:
            raise ValueError("La note maximale doit être un nombre !")

        if note_max <= 0:
            raise ValueError("La note maximale doit être supérieure à 0 !")

        self.type_eval = type_eval 
        self.titre = titre.strip()
        self.date = date.strip()
        self.coefficient = coefficient
        self.note_max = note_max

class Grade:

    def __init__(self, note):
        try:
            note = float(note)
        except:
            raise ValueError("La note doit être un nombre !")

        if note < 0 or note > 20:
            raise ValueError("La note doit être entre 0 et 20 !")

        self.note = note

class Database:

    def __init__(self, db_name):
        self.db_name = db_name 
        self.create_tables()

    def connect(self):
        return sqlite3.connect(self.db_name)
    
    def create_tables(self):
        conn = self.connect()        
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                cne      TEXT UNIQUE NOT NULL,
                nom      TEXT NOT NULL,
                prenom   TEXT NOT NULL,
                groupe   TEXT NOT NULL,
                filiere  TEXT NOT NULL,
                email    TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                type_eval   TEXT NOT NULL,
                titre       TEXT NOT NULL,
                date        TEXT,
                coefficient REAL DEFAULT 1.0,
                note_max    REAL DEFAULT 20.0
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS grades (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id    INTEGER NOT NULL,
                evaluation_id INTEGER NOT NULL,
                note          REAL NOT NULL,
                UNIQUE(student_id, evaluation_id),
                FOREIGN KEY(student_id)    REFERENCES students(id),
                FOREIGN KEY(evaluation_id) REFERENCES evaluations(id)
            )
        """)
        conn.commit()
        conn.close()

    def add_student(self, student):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO students (cne, nom, prenom, groupe, filiere, email)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (student.cne, student.nom, student.prenom,
              student.groupe, student.filiere, student.email))

        conn.commit()
        conn.close()

    def update_student(self, student_id, student):

        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            UPDATE students
            SET cne=?, nom=?, prenom=?, groupe=?, filiere=?, email=?
            WHERE id=?
        """, (student.cne, student.nom, student.prenom,
              student.groupe, student.filiere, student.email,
              student_id))

        conn.commit()
        conn.close()
    
    def delete_student(self, student_id):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM grades WHERE student_id=?", (student_id,))
        cur.execute("DELETE FROM students WHERE id=?", (student_id,))
        conn.commit()
        conn.close()

    def get_all_students(self, search=""):
        conn = self.connect()
        cur = conn.cursor()

        if search.strip() != "":
            search = search.strip().lower()

            cur.execute("""
                SELECT id, cne, nom, prenom, groupe, filiere, email
                FROM students
                WHERE lower(cne)    LIKE ?
                   OR lower(nom)    LIKE ?
                   OR lower(groupe) LIKE ?
                ORDER BY nom, prenom
            """, ("%" + search + "%",
                  "%" + search + "%",
                  "%" + search + "%"))
        else:
            cur.execute("""
                SELECT id, cne, nom, prenom, groupe, filiere, email
                FROM students
                ORDER BY nom, prenom
            """)

        rows = cur.fetchall()
        conn.close()
        return rows  

    def add_evaluation(self, evaluation):
        conn = self.connect()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO evaluations (type_eval, titre, date, coefficient, note_max)
            VALUES (?, ?, ?, ?, ?)
        """, (evaluation.type_eval, evaluation.titre, evaluation.date,
              evaluation.coefficient, evaluation.note_max))

        conn.commit()
        conn.close()

    def delete_evaluation(self, evaluation_id):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM grades WHERE evaluation_id=?", (evaluation_id,))
        cur.execute("DELETE FROM evaluations WHERE id=?", (evaluation_id,))

        conn.commit()
        conn.close()
    
    def get_all_evaluations(self):
        conn = self.connect()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, type_eval, titre, date, coefficient, note_max
            FROM evaluations
            ORDER BY id DESC
        """)

        rows = cur.fetchall()
        conn.close()
        return rows
    
    def save_grade(self, student_id, evaluation_id, grade):
        conn = self.connect()
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO grades (student_id, evaluation_id, note)
                VALUES (?, ?, ?)
            """, (student_id, evaluation_id, grade.note))

        except sqlite3.IntegrityError:
            cur.execute("""
                UPDATE grades
                SET note=?
                WHERE student_id=? AND evaluation_id=?
            """, (grade.note, student_id, evaluation_id))

        conn.commit()
        conn.close()
    
    def delete_grade(self, grade_id):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM grades WHERE id=?", (grade_id,))
        conn.commit()
        conn.close()

    def get_all_grades(self):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT g.id, s.cne, s.nom, s.prenom, e.titre, e.type_eval, g.note
            FROM grades g
            JOIN students s    ON s.id = g.student_id
            JOIN evaluations e ON e.id = g.evaluation_id
            ORDER BY s.nom, s.prenom
        """)
        rows = cur.fetchall()
        conn.close()
        return rows

    def get_students_for_dropdown(self):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT id, cne, nom, prenom FROM students ORDER BY nom, prenom")
        rows = cur.fetchall()
        conn.close()
        return rows

    def get_evaluations_for_dropdown(self):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT id, type_eval, titre FROM evaluations ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        return rows

    def get_student_average(self, student_id):
        conn = self.connect()
        cur = conn.cursor()

        cur.execute("""
            SELECT g.note, e.coefficient, e.note_max
            FROM grades g
            JOIN evaluations e ON e.id = g.evaluation_id
            WHERE g.student_id = ?
        """, (student_id,))

        rows = cur.fetchall()
        conn.close()

        if len(rows) == 0:
            return None

        total = 0.0        # somme de (note_sur_20 * coefficient)
        total_coef = 0.0   # somme des coefficients

        for note, coef, note_max in rows:
            if note_max != 20:
                note = (note / note_max) * 20

            total = total + (note * coef)    # on accumule
            total_coef = total_coef + coef   # on accumule le coefficient

        if total_coef == 0:
            return None

        moyenne = total / total_coef
        return moyenne

    def export_to_json(self, filepath):
        data = {}

        data["students"] = []
        for row in self.get_all_students():
            student_dict = {
                "id":      row[0],
                "cne":     row[1],
                "nom":     row[2],
                "prenom":  row[3],
                "groupe":  row[4],
                "filiere": row[5],
                "email":   row[6]
            }
            data["students"].append(student_dict)

        data["evaluations"] = []
        for row in self.get_all_evaluations():
            eval_dict = {
                "id":          row[0],
                "type_eval":   row[1],
                "titre":       row[2],
                "date":        row[3],
                "coefficient": row[4],
                "note_max":    row[5]
            }
            data["evaluations"].append(eval_dict)

        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT id, student_id, evaluation_id, note FROM grades")
        data["grades"] = []
        for row in cur.fetchall():
            grade_dict = {
                "id":            row[0],
                "student_id":    row[1],
                "evaluation_id": row[2],
                "note":          row[3]
            }
            data["grades"].append(grade_dict)
        conn.close()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_from_json(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f) 

        conn = self.connect()
        cur = conn.cursor()

        cur.execute("DELETE FROM grades")
        cur.execute("DELETE FROM evaluations")
        cur.execute("DELETE FROM students")
        conn.commit()

        for s in data.get("students", []):
            cur.execute("""
                INSERT INTO students (id, cne, nom, prenom, groupe, filiere, email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (s["id"], s["cne"], s["nom"], s["prenom"],
                  s["groupe"], s["filiere"], s.get("email", "")))

        for e in data.get("evaluations", []):
            cur.execute("""
                INSERT INTO evaluations (id, type_eval, titre, date, coefficient, note_max)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (e["id"], e["type_eval"], e["titre"], e.get("date", ""),
                  e["coefficient"], e["note_max"]))

        for g in data.get("grades", []):
            cur.execute("""
                INSERT INTO grades (id, student_id, evaluation_id, note)
                VALUES (?, ?, ?, ?)
            """, (g["id"], g["student_id"], g["evaluation_id"], g["note"]))

        conn.commit()
        conn.close()