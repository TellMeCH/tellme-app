# Application Data Model

The Django app `call_miner` is meant to organize and serve the data model shown below:

![Application Data Model](images/Application_Data_Model.drawio.svg)

Some points about Users, Employees, Analysts, and Agents:
* An Employee is just a user that is linked to an Organization and has a role. This role can either be "Analyst" or "Agent".
* Since Agents and Analysts inherit from the Employee class, they share their ID with the Employee instance.
* An Agent is a special type of Employee, because it can be attached to a Conversation.
* Agents have hierarchical relationships among themselves, resulting in one being the manager of another.
* On the other hand, an Analyst is just an Employee that can't appear in Conversations, and has special edit access to Topics.
* Any Employee can also be an Organization Admin, with permissions to edit and create Employee instances and OrganizationAPIKeys