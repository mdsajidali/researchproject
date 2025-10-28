# OpenShift Deployment Notes

1. Log in:
   ```bash
   oc login --token=<token> --server=<url>
2. Create a new project
oc new-project expense-tracker
3. Deploy Postgres:
oc apply -f postgres.yaml
4. Deploy Django app:
oc apply -f deployment.yaml
oc apply -f service.yaml
oc apply -f route.yaml
5. get app URL:
oc get routes
6. Open the given URL in a browser.
