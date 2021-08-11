# azure storage account
for i in {1..9}
do
 java -jar azure-function-examples $i
done

# azure serverless sql
for i in {20..24}
do
 java -jar azure-function-examples $i
done