// Create DB and collection
db = new Mongo().getDB("database");
db.createCollection("Registry");
db.Registry.insertOne({ "_id"  : 1,
                        "eax" : "test_eax",
                        "ebx" : "test_ebx",
                        "ecx" : "test_ecx", 
                        "edx" : "test_edx",
                        "ebp" : "test_ebp",
                        "esp" : "test_esp",
                        "edi" : "test_edi",
                        "eip" : "test_eip",
                        "cs" : "test_cs",
                        "ds" : "test_ds",
                        "es" : "test_es",
                        "fs" : "test_fs",
                        "gs" : "test_gs",
                        "ss" : "test_ss",
                        "eflags" : "test_eflags"});




db.createCollection("Parametrs");
db.Parametrs.insertOne({"_id":1, "output" : "test_output", "registry" : { "$ref" : "Registry", "_id" : 1}})





db.createCollection("Tasks");
db.Tasks.createIndex(
    { "name":1},
    {"unique":true}
);
db.Tasks.insertOne({
    "_id": 1,
    "name":"task_name",
    "description":"description",
    "difficulty":5,
    "success":0, 
    "stack" :{"first":"first_stack","second":"second_stack"},
     "tests": {"first":"false","second":"false_too"},
     "parameters" : {"$ref":"Parametrs", "_id": 1}
});

db.createCollection("LTI_sessions");
db.LTI_sessions.insertOne({
    "_id":"uniq_id_lti",
    "datetime":  ISODate("2014-02-10T10:50:42.389Z"),
    "tasks":{"fist":"fr", "second":"sec"},
    "role": ["student"]
});


db.createCollection("Codes");
db.Codes.insertOne({
    "_id":"uniq_id_codes",
    "created":  ISODate("2055-02-10T10:50:42.389Z"),
    "last_update ":  ISODate("1984-02-10T10:50:42.389Z"), 
    "code":"int main{return 404;}",
    "breakpoints":[15,14,00],
    "arch":"what is it arch?engish is good", 
    "lti_user": { "$ref" : "LTI_sessions", "_id" : "uniq_id_lti"}
});


db.createCollection("Solutions");
db.Solutions.insertOne({
    "_id":1,
    "datetime":ISODate("2077-02-10T10:50:42.389Z"),
    "feeadback":"Is is awesome, my memories are immortable",
    "task":{ "$ref" : "Tasks", "_id" : 1},
    "LTI_session": { "$ref" : "LTI_sessions", "_id" : "uniq_id_lti"},
    "codes":{ "$ref" : "Codes", "_id" : "uniq_id_codes"},
});


db.createCollection("Consumers");
db.Consumers.insertOne({
    "_id":"Consumer_id",
    "secret":"I cannot keep a secret",
    "datetime":ISODate("2077-02-10T10:50:42.389Z"),
    "timestampl":[1,2,3,4]

});


db.createCollection("Logs");
db.Logs.insertOne({
    "_id":"Uniq_logs_id",
    "time" : ISODate("2077-02-10T10:50:42.389Z"),
    "levelname" : "this is bottom",
    "message" : "Who is John Galt?",
    "lineno" : 2902,
    "pathname" : "/home/seckret/passwords",
    "meta" : {
        'indexes': ['time']
    }
});

db.createCollection("Role");
db.Role.insertOne({
    "name" : "genius",
    "description" : "buy a dollar for 130"
});    


db.createCollection("User");
db.User.insertOne({
    "_id" : "User_id",
    "username" : "Maximyss III",
    "datetime" :  ISODate("2012-02-10T10:50:42.389Z"),
    "tasks" : {"fist":"fr", "second":"sec"},
    "roles" :[{ "$ref" : "Role", "name" : "genius"}],
    "active" : true
});    
    




