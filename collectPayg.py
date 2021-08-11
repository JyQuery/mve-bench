from insight import insightQuery
import json


# for payg plan
functionList = {
    'PlayerOperation':
        {
            'applicationId': '16de91e7-0fa7-49a4-b29c-a5ca34468d07',
            'apiKey': '1sr423hpy2bupdyf0czlusw8fsjmfigus7gtl1du'
        }, 'PlayerOperationDb':
        {
            'applicationId': '16de91e7-0fa7-49a4-b29c-a5ca34468d07',
            'apiKey': '1sr423hpy2bupdyf0czlusw8fsjmfigus7gtl1du'
        }
}
functionName = "PlayerOperation"
res = insightQuery(functionList, functionName, 'P10D', '2021-07-14 08:55:28', endTime='2021-07-15 18:40:39'
                   , table='requests')
print(res)
fileName = "result/exp1.5.premium.sql.2h/function-{}-requests".format(functionName)
with open(fileName, "w") as f:
    json.dump(res["tables"][0], f)
print(len(res["tables"][0]["rows"]))