# User Onboarding Flow

Employees of an organization are to be managed by the organization admins. As such, admins have the possibility of registering new agent or analyst accounts.

Agent accounts will then potentially appear linked to existing conversations, and analyst accounts will have the ability to modify or create topics.

The process to onboard a new user account is as follows:
1. The organization admin makes a POST request to the /api/v1/employees/ endpoint, with data of the following format:
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
3. If the authentication type was set to "password", the onboarding email will contain a password reset link. Users will then specify their password via that link, and it will be stored in Firebase. With other authentication types, the link will simply redirect to the app's home page.
4. After this setup, users can normally log in to the app.