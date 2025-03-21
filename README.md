# Zuora Deployment Automation Utility Tool

Zuora deployment automation is designed to help with the tracking of the source code and configuration in Zuora (version control) and to help with the deployment to other environments, reducing manual work. \

# Get started
To get started, you need two repositories:
- [zuoradevtools](...): this is the deployment automation utility tool.
- [zuora-vcs](...): this is your repository that tracks Zuora content.

Then, install the required dependencies in your Python virtual environment by running:
```sh
cd zuora-devtools
pip install -r requirements.txt
```

Additionally, you need a credentials file ``sm.json`` to ``$HOME/.zuora/``. \
You can include credentials for different environments. Valid environments names, as of now, are:
- dev
- qa
- uat
- prod


The ``sm.json`` file structure is the following:
```json
{
    "${environment_name}": {
        "comment": "string",
        "zuora_api_base_url": "string",
        "zuora_api_version": "string",
        "zuora_client_id": "string",
        "zuora_client_secret": "string",
        "zuora_client_grant_type": "string",
        "zuora_bearer_token": "",
        "zuora_token_ttl": ""
    }
}
```

In the future, the secrets management will be improved and decoupled through [common/lib/secrets_manager.py](common/lib/secrets_manager.py)

Zuora deployment automation consists of 3 steps, which are described in detail below:
- Step1. Extract state
- Step2. Plan your deployment
- Step3. Deploy


## Step 1: Extract
To open the GUI for Extract step, use:

```sh
python extract.py
```
From the GUI, it is possible to select which components to extract (e.g. Custom fields, Workflows, Billing document templates, etc.).

``🟣 Extract`` button extracts data from Zuora into ``Zuora-VCS`` repository. 
After the data extraction has finished, developers can check their changes in ``Zuora-VCS`` repository, commit and push to their ``feature branch``.

## Step 2 and 3: Plan & Deploy
To open the GUI for Plan & Deploy step, use:

```sh
python plan_deploy.py
```

From the GUI, it is possible to select which components to include in the deployment plan, and the target environment for deployment.

``🟡 Plan`` button prepares the data to be deployed to Zuora target environment. The output of this step is stored in ``zuora-vcs/temp`` directory, which is not version controlled. It is a staging directory.\
After plan is finished, ``make sure to check the temp folder before deploying``. You can remove components that you don't want to deploy. For example, if under ``zuora-vcs/temp/billing_documents/`` you see a template that you don't want to deploy (e.g. Generic Invoice template), you can delete from that folder before pressing the ``Deploy`` button.

``🟢 Deploy`` button uses the data prepared by deployment plan from the ``zuora-vcs/temp`` folder and using ZuoraAPI it publishes to the target environment. 


# Next steps:

- Custom Fields (standard objects)
    - ✅ Remove Configuration templates usage for Custom Field (standard objects) (non-consistent behavior when running sync)
    - 🟡 Synchronize all environments (e.g. custom fields should be consistent, including labels, description, etc.)
    - 🟡 Implement functionalities through Zuora API:
        - ✅ export
        - ✅ plan (diff)
        - deploy (add, update, delete)
    - 🟡 Test and enable from GUI

- Custom Objects definition
    - ✅ Remove Configuration templates usage for Custom Object definition (non-consistent behavior when running sync)
    - 🟡 Synchronize all environments (e.g. object fields should be consistent, including labels, description, etc.)
    - 🟡 Implement functionalities through Zuora API:
        - ✅ export
        - ✅ plan (diff)
        - deploy (add, update, delete)
    - 🟡 Test and enable from GUI

- Custom Objects records 
    - 🟡 Synchronize all environments (e.g. records should be consistent)
    - ✅ Implement functionalities through Zuora API:
        - ✅ export
        - ✅ plan (diff)
        - ✅ deploy
        plan and deploy functionalities through Zuora API
    - 🟡 Test and enable from GUI

- E-Invoicing (business regions and templates)
    - 🟡 (high priority) Implement export, plan and deploy functionalities through Zuora API

- Notifications & Callouts
    - ✅ Remove Configuration templates usage (little experience and not positive feedback)
    - 🟡 (low priority) Implement export, plan and deploy functionalities through Zuora API

- Taxation Settings
    - ✅ Remove Configuration templates usage (little experience and not positive feedback)
    - ✅ For now, we don't need this (we barely change it)








