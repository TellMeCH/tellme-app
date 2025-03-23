# User Onboarding Flow

Employees of an organization are to be managed by the organization admins. As such, admins have the possibility of registering new agent or analyst accounts.

Agent accounts will then potentially appear linked to existing conversations, and analyst accounts will have the ability to modify or create topics.

The process to onboard a new user account is as follows:

### Authentication with Email + Password
1. The organization admin makes a POST request to the /api/v1/employees/ endpoint, with payload in the following format:
    ```json
    {
        "role": "ANALYST",
        "organization": "1",
        "is_organization_admin": false,
        "user": {
            "email": "analyst@acme.org",
            "first_name": "John",
            "last_name": "Doe",
            "auth_type": "password"
        }
    }
    ```
2. This will create a new Employee instance in the organization, and will also instantiate a user account with Firebase. Also, an onboarding email will be sent to the user.
3. This onboarding email will contain a password reset link. Users will then specify their password via that link, and it will be stored in Firebase.
4. After this setup, users can normally log in to the app.

### Authentication with Identity Providers (Google, Microsoft)
1. The organization admin makes a POST request to the /api/v1/employees/ endpoint, with payload in the following format:
    ```json
    {
        "role": "ANALYST",
        "organization": "1",
        "is_organization_admin": false,
        "user": {
            "email": "analyst@acme.org",
            "first_name": "John",
            "last_name": "Doe",
            "auth_type": "microsoft"
        }
    }
    ```
2. This will create a new Employee instance in the organization, but will not yet instantiate a user account with Firebase. As before, an onboarding email will be sent to the user.
3. This onboarding email will contain a link to the app's frontend, where users will log in with their selected IdP
4. On this first login, a new Firebase user instance will be created. However, if the user's email has not been automatically validated by Firebase, an email verification request will be sent, and the login will be blocked.
5. After this setup, validating the user email if necessary, users can normally log in to the app.