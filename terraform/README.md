# Infrastructure as Code

## Reproducing
1. There's a module that needs to be run *one* time (sets up storage for Terraform state, and creates a pool and providers to connect GitHub to the app)
2. The other is run every time we push to staging or prod.