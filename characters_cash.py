import ps
import sqlite3

class PaladinsDatabase:
    def __init__(self, db_file):
        self.db_file = db_file
        self._create_tables()

    def _create_tables(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS champions
                     (champion_id INTEGER PRIMARY KEY, 
                      champion_name TEXT, 
                      champion_avatar TEXT,
                      champion_role TEXT)''')
        conn.commit()
        conn.close()

    def update_champions(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        champions = ps.GetChampions()

        # Добавляем каждого персонажа в базу данных
        for champion in champions:
            champion_id = champion['id']
            champion_name = champion['Name']
            champion_avatar = champion['ChampionIcon_URL']
            champion_role = champion['Roles'].split()[-1]

            c.execute("SELECT * FROM champions WHERE champion_id = ?", (champion_id,))
            existing_champion = c.fetchone()

            if existing_champion:
                # Если запись существует, обновляем остальную информацию
                c.execute(
                    "UPDATE champions SET champion_name = ?, champion_avatar = ?, champion_role = ? WHERE champion_id = ?",
                    (champion_name, champion_avatar, champion_role, champion_id))
            else:
                # Если запись не существует, создаем новую запись в базе данных
                c.execute(
                    "INSERT INTO champions (champion_id, champion_name, champion_avatar, champion_role) VALUES (?, ?, ?, ?)",
                    (champion_id, champion_name, champion_avatar, champion_role))

        # Сохраняем изменения и закрываем соединение с базой данных
        conn.commit()
        conn.close()

    def get_cashed_champions(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('SELECT champion_id, champion_name, champion_avatar, champion_role FROM champions')
        cashed_champions = c.fetchall()
        conn.close()
        return cashed_champions

    def get_lite_champion(self, champion_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('SELECT champion_name, champion_avatar, champion_role FROM champions WHERE champion_id = ?', (champion_id,))
        lite_champion = c.fetchone()
        conn.close()
        return lite_champion