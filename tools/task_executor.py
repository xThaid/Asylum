from datetime import datetime
import action_sender

import db

conn = db.create_connection()

try:
    cur = conn.cursor()
    now = datetime.now().timestamp()
    rows = cur.execute("SELECT * FROM blinds_task \
        WHERE time <= ?", (int(now),)).fetchall()
    for row in rows:
        status = -1
        if (now - row[1]) < row[6]:
            action_sender.send(row[2], row[3])
            status = 1
        else:
            status = 0

        cur.execute("INSERT INTO blinds_task_history \
            (time, device, action, user_id, status) VALUES \
            (?, ?, ?, ?, ?)", (int(now), row[2], row[3], row[4], status))
        cur.execute("DELETE FROM blinds_task WHERE id = ?", (row[0],))
finally:
    conn.commit()
    conn.close()
