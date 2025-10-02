# Mesos/Marathon Deployment Notes

1. Start Mesos and Marathon.
2. Deploy Postgres first:
   ```bash
   curl -X POST http://localhost:8080/v2/apps -d @postgres.json -H "Content-Type: application/json"
3. Deploy Expense Tracker app:
curl -X POST http://localhost:8080/v2/apps -d @expense.json -H "Content-Type: application/json"
4. Status
curl http://localhost:8080/v2/apps | jq .
