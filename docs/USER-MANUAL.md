# EclecticIQ Intelligence Center App for QRadar

# 1. Introduction

## 1.1 Prerequisites

1. QRadar On-prem version 7.3.3 Patch 6. Reference: [Qradar Installation Guide](https://www.ibm.com/docs/SS42VS_7.3.2/com.ibm.qradar.doc/b_siem_inst.pdf)
2. EclecticIQ Intelligence Center 2.12 (or EclecticIQ Intelligence Center 2.11 with `eclecticiq-extension-api` Extension installed)
3. Outgoing feeds should be set up on EclecticIQ Intelligence Center.
4. API key generated from EclecticIQ Intelligence Center.
5. User should have the following permissions in EclecticIQ Intelligence Center to authenticate: `read permissions`, `read entities`, `modify entities`, `read extracts`, `read outgoing-feeds`

## 1.2 Installation

### 1.2.1 EclecticIQ Intelligence Center

#### Step 1. Configure the outgoing feed(s) you wish to use with the QRadar App

Configure the Outgoing Feeds by following the instructions in the [EclecticIQ Intelligence Center User Guide](https://docs.eclecticiq.com/).

### 1.2.2 QRadar 

#### Step 1. Download the QRadar App from XForce

TODO

#### Step 2. Navigate to QRadar App and select extension management

![Navigate to QRadar App and select extension management](/docs/assets/install-qradar-select-management.png)

#### Step 3. Browse the file and install the application

![Browse the file and install the application](/docs/assets/install-qradar-the-application.png)

#### Step 4. App should be installed successfully

![Browse the file and install the application](/docs/assets/install-qradar-success.png)

# 2. Setup

## 2.1 Connection to the EclecticIQ Intelligence Center

After the installation, the user will have to provide details below in the setup page and click the “Test connection” button. 

* Name (Required)
* Host (Required): Host should be entered as `https://<hostname>/api/<version>`
* API key (Required)
* QRadar Security token (Required)

![Setup success](/docs/assets/setup-success.png)

Once the connection is successful, the user will have to click on the “Save” button to save the configuration.

![Save setup](/docs/assets/setup-save.png)

### 2.2 Configuration of the Observables and Ingest Data

After saving the credentials, the user will have to enter the below details and click on save.

* Select one or more outgoing feeds to collect observables data. (Required)
* Select observable time to live. Default (Required)
* Select first run backfill historical data time. (Required)
* Select the observable types to ingest. (Required)
* Select the interval to collect the observables. (Required)

![Setup feeds](/docs/assets/setup-feeds.png)

Setup page will show a message that shows the last poll date for Observable ingestion.

![Setup feeds](/docs/assets/setup-feeds-2.png)

Note: 

* Maximum of four Outgoing feeds to ingest can be selected
* Minimum interval time to collect the observables should be 3600s

# 4. Reference Table Validation

Reference table are created based on the “Select one or more Outgoing feeds to ingest " & "Observable types to ingest " 

Ex: If user selects "Select one or more Outgoing feeds to ingest "  as Poll Taxii Stand & "Observable types to ingest "  as email & IP
2 reference tables should be created.

Reference table-1 should collect data of Poll Taxi stand in the email type
Reference table-2 should collect data of Poll Taxi stand in the Ip type

Initially there should be no reference table when the API is triggered

![Postman reference example](/docs/assets/reference-table-postman-ex-1.png)

The reference tables should be created when the configuration is saved and the API should be triggered with 200 status codes.

![Postman reference example](/docs/assets/reference-table-postman-ex-2.png)

![Reference table logs](/docs/assets/reference-table-logs.png)

To Verify the data in the reference table

![Verify the data in the reference table](/docs/assets/reference-table-verify.png)

# 5. Sighting Creation

Step 1. Navigate to the Log activity tab in the QRADAR and right click on the source ip/ destination ip.

![Sighting creation](/docs/assets/sighting-creation-manual.png)

Step2:- A pop-up window will appear to ask for the details below. 

Clicking on save will create sightings in the EIQ platform with provided details.

* Sighting Value: Value which is clicked
* Sighting type: Type of sighting. Possible values: ip, domain, url, email, hash
* Sighting title: Title of sighting
* Sighting description: Description of sighting
* Sighting confidence: Confidence of sighting. Possible values: low, medium, high
* Sighting tags delimited by a comma: Any tags to attach with sighting

![Sighting creation detail](/docs/assets/sighting-creation-detail.png)

![Sighting creation success](/docs/assets/sighting-creation-success.png)

Step 3:- Verify the sighting in the EIQ application

![Sighting creation verify](/docs/assets/sighting-creation-verify.png)

# 6. Lookup (observable Table and creation of sighting)

Step1:- Navigate to the Log activity tab in the QRADAR and right click on the source ip/ destination ip.

![Log activity](/docs/assets/lookup-1.png)

Step2:- A pop-up window will appear 

![Lookup popup](/docs/assets/lookup-2.png)

Step 3:-Click on create sighting button and verify the success message

![Lookup success](/docs/assets/lookup-3.png)

Step 4:- Verify the sighting in the EIQ application

![Lookup verify](/docs/assets/lookup-4.png)

# 7. Custom Sighting Creation 

The following example creates an alert rule using ingested threat intelligence data in QRadar:

This rule is connected to Destination IPs in log events and ingested IP related threat intelligence data.

1. In QRadar, click the Offenses tab.
2. Click Rules > Actions > New Event Rule.
3. In the Rule wizard, select the Events radio button, and click Next.
4. Locate when Reference Table Key data matches any|all selected event properties and selected reference table column Select operator the value of selected event property in the list of tests, and click to add this test to the rule.
	* Assign values to place holders by clicking on the following underlined parameters:
	* Click Reference Table Key > eiq_data_ip > eiq_value > Submit. This creates a rule for IP address matching.
	* Click Selected event properties > Source IP > ＋ > Submit.
	* Click Selected reference table column > value > Submit.
	* Click Select operator > Equals > Submit.
	* Click Selected event property. For example: Destination IP
5. Click Next.
6. Select the checkbox for “Execute Custom Action”
	* Select Action related to the data type of the rule created. For example if a rule is created for matching Destination IP select custom action as eiq_sighting_d_ip. 
7. Click Finish.

![](/docs/assets/sighting-1.png)

![](/docs/assets/sighting-2.png)

![](/docs/assets/sighting-3.png)

![](/docs/assets/sighting-4.png)

# 8. Deletion of data 

## Manual deleting the data

Deletion of observables will be performed when the user clicks the button to delete the data in the setup page. While the user will click on this option, the app will make an API call to Delete reference tables of Qradar and all tables created for that feed will be deleted along with the schema. Once deleted recovery will not be possible

![](/docs/assets/delete-1.png)

## Auto deletion of the data

In the configuration screen, users will be able to select the retention period from the field “Select observable time to live”. One scheduled script will be running in the backend every day to remove the data which was updated before the retention period. 

![](/docs/assets/delete-2.png)

# 9. Dashboard

Once the sighting is created from Qradar either by custom rule or manually by the user, a record of that will be stored in a custom DB in the app. Dashboard will be populated using stored sighting data. Below three widgets will be loaded.

1. Sightings by time (histogram) 
2. Sighting by Confidence (bar chart) 
3. Sighting by type count (bar chart) 

![](/docs/assets/dashboard.png)

10. Tips & Tricks

How to create Custom Rules: https://www.ibm.com/docs/en/qsip/7.4?topic=rules-creating-custom-rule

How to check the logs: 

1. Login to backend of Qradar instance
2. Connect to the container of the EIQ application
3. Go to opt/app-root/store/log
4. Check startup.log or app.log