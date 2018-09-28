from datetime import datetime
import asylumd_client

import db

conn = db.create_connection()

try:
    cur = conn.cursor()
    now = datetime.now().timestamp()
    rows = cur.execute("SELECT * FROM blinds_task \
        WHERE time <= ?", (int(now),)).fetchall()
    for row in rows:
        if (now - row[1]) < row[6]:
            shutter_id = row[2] - 1
            action_id = row[3] - 1
            asylumd_client.shutterAction(shutter_id, action_id)
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
