import pyodbc

constr = 'DSN=MJ_DMS;UID=MHGROUP;PWD=mhdocs'

def check_lock(doc_number):
  locked_by = ''
  
  con = pyodbc.connect(constr)
  cursor = con.cursor()
  cursor.execute('SELECT LOCKUSER FROM dbo.MJ_ScanLock WHERE DOCNUM = {}'.format(doc_number))
  results = cursor.fetchone()
  if results:
    locked_by = results[0]
  
  con.close()
  
  return locked_by
  
def lock_scan(doc_number, username):
  con = pyodbc.connect(constr)
  cursor = con.cursor()
  cursor.execute('INSERT INTO dbo.MJ_ScanLock (DOCNUM, LOCKUSER) VALUES (?,?)', [doc_number, username])
  con.commit()
  con.close()
  
def unlock_scan(doc_number):
  con = pyodbc.connect(constr)
  cursor = con.cursor()
  cursor.execute('DELETE FROM dbo.MJ_ScanLock WHERE DOCNUM = ?', [doc_number])
  con.commit()
  con.close()
  
def get_assistants(author):
  con = pyodbc.connect('DRIVER={SQL Server};SERVER=GR-SQL-02;DATABASE=Staff;UID=hssql;PWD=nFcv0ln1gQJ2V0PDXCbf')
  cursor = con.cursor()
  cursor.execute("SELECT t.tAccountName AS TimekeeperId, e.SecAccountName AS SecId FROM vSecretaryAssignment_with_Exceptions e JOIN vTimekeeper t ON t.STAFFID = e.TimeKeeperID WHERE t.tAccountName = '{}'".format(author))
  results = cursor.fetchall()
  con.close()

  return ','.join(['{}@millerjohnson.com'.format(r.SecId) for r in results])