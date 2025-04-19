import json

a = ["NS001120 :",
     {"ARMA":{"sap":1, "fact":2, 'delta': -1},
      "FXED":{"sap": 0,"fact":1},
      "FRMF":{"sap":0, "fact":1}
      }]

print(json.dumps(a))