/*
  Very basic Javascript in-memory deserializer.
  =======================================================================
  Check out this thing for stuff:
  https://sqlite.org/wasm/doc/trunk/cookbook.md#impexp
  =======================================================================
  **Uncomment** the lambda at the bottom for testing.

  Based on:
  =========
  2022-09-19

  The author disclaims copyright to this source code.  In place of a
  legal notice, here is a blessing:

  *   May you do good and not evil.
  *   May you find forgiveness for yourself and forgive others.
  *   May you share freely, never taking more than you give.

  ***********************************************************************

  A basic demonstration of the SQLite3 "OO#1" API.
*/

'use strict';
class Sqlite3DES {
  constructor() {
    this.db = null;
    this.error = "";
  }

  static async init() {
    var sapi = new Sqlite3DES();
    return sapi;
  }

  lastError() {
    return this.error;
  }

  deserialize(data){
    if(this.db != null){
      this.db.close();
    }
    const capi = globalThis.sqlite3.capi /*C-style API*/,
            oo = globalThis.sqlite3.oo1  /*high-level OO API*/;
    this.db = new globalThis.sqlite3.oo1.DB();
    const p = globalThis.sqlite3.wasm.allocFromTypedArray(data);
    var res_val = capi.sqlite3_deserialize(this.db.pointer, 'main', p, data.byteLength, data.byteLength, capi.SQLITE_DESERIALIZE_RESIZEABLE | capi.SQLITE_DESERIALIZE_FREEONCLOSE);
    this.db.checkRc(res_val);
  }

  serialize(){
    if(this.db == null){
      this.error = "Database is null. Initialize first!";
      return [];
    }
    const capi = globalThis.sqlite3.capi /*C-style API*/,
            oo = globalThis.sqlite3.oo1  /*high-level OO API*/;
    return capi.sqlite3_js_db_export(this.db);
  }

  select(stmt){
    this.error = "";

    if(this.db == null) {
      this.error = "Database is null. Initialize first!";
      return [];
    }
    var result = [];
    try {
      this.db.exec({
        sql: stmt,
        rowMode: 'array', // 'array' (default), 'object', or 'stmt'
        callback: function(row){
          result.push(row)
        }
      });
    } catch(error) {
      this.close();
      this.error = `Something went badly wrong: [${error}]'`;
      return [];
    }
    return result;
  }

  close(){
    if(this.db != null){
      this.db.close();
      this.db = null;
    }
  }
}

async function initJS(){
    var dbObj = Sqlite3DES.init();
    return dbObj;
}

async function testRunJS(dbObj) {
    try {
        console.log("1. Calling test server...");
        const response = await fetch('http://127.0.0.1:8180/testbin/86');
        console.log("2. Got response from test call...");
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        console.log("3. Converting results to buffer...");
        const data = await response.arrayBuffer();
        console.log(`4. Received data length: ${data.byteLength} => deserialize...`);    
        dbObj.deserialize(data);
        console.log("5. Deserialized data...");
        const re_data = dbObj.serialize();
        console.log(`6. Deserialized data has size ${re_data.byteLength}`);
        console.log("7. There is no 7...");
    } catch (error) {
        console.error('8. TestRun fetch error:', error);
        dbObj.close();
        throw new Error(`9. TestRun fetch error: ${error}`);
    }
    console.log("10. Trying to run select stmt...");
    try {
      var res = dbObj.select("select * from Binary;");
      console.log("11. Printing results...");
      res.forEach((x) => console.log(x));
      console.log("12. Attempting to close the database...");
      dbObj.close();
      console.log("13. Database closed...");
      return res;
    } catch (error) {
        console.log("14. Something happened, attempting to close...");
        dbObj.close();
        console.error('TestRun db exec error:', error);
        throw new Error(`testRun db exec error: ${error}`);
    }
}

/**
 * This one is called from index.html of the Flutter App and initializes sqlite3.
 * @returns Nothing
 */
async function initSqlite() {
  var sqlite3 = await globalThis.sqlite3InitModule({
    /* We can redirect any stdout/stderr from the module like so, but
      note that doing so makes use of Emscripten-isms, not
      well-defined sqlite APIs. */
    print: console.log,
    printErr: console.log
  });
  return sqlite3;
}

/**
 * Uncomment this bit of code if you want to run server.py to test out new stuff
 */
// ( async () => {
//   globalThis.sqlite3 = await initSqlite();
//   var db = await initJS();
//   await testRunJS(db);
// })();