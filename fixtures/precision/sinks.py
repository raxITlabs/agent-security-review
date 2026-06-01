# Precision fixture for stop.llm-output-to-dangerous-sink (broadened from the old
# single `cursor.execute(f"...")` literal to the real code/shell/SQL sink set).

import os, subprocess

def run_model_code(resp):
    eval(resp.content)                                 # EXPECT_MATCH:stop.llm-output-to-dangerous-sink

def exec_output(text):
    exec(text)                                          # EXPECT_MATCH:stop.llm-output-to-dangerous-sink

def shell_it(cmd):
    os.system(cmd)                                      # EXPECT_MATCH:stop.llm-output-to-dangerous-sink

def shell_sub(cmd):
    subprocess.run(cmd, shell=True)                     # EXPECT_MATCH:stop.llm-output-to-dangerous-sink

def sql_fstring(conn, name):
    conn.execute(f"SELECT * FROM users WHERE name='{name}'")  # EXPECT_MATCH:stop.llm-output-to-dangerous-sink

# Safe forms — must NOT fire.
def safe_sub(cmd_list):
    subprocess.run(cmd_list)                            # EXPECT_NONE:stop.llm-output-to-dangerous-sink

def safe_sql(conn, name):
    conn.execute("SELECT * FROM users WHERE name=%s", (name,))  # EXPECT_NONE:stop.llm-output-to-dangerous-sink

def safe_json(data):
    import json
    return json.loads(data)                             # EXPECT_NONE:stop.llm-output-to-dangerous-sink
