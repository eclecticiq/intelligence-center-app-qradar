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

You can connect the QRadar App to one or more outgoing feeds in the Intelligence Center.

When configuring an outgoing feed you should set the transport type to `EclecticIQ Entities CSV`.

It is also important that the authenticated user (the user whose API key is being used in the add-on) has the correct permissions to access all the datasets used in the outgoing feed AND the workspaces that these data sets belong too.

A common error seen is that a user does not have access to read either the datasets and/or the workspaces these datasets belong to for an outgoing feed configured in QRadar. An easy way to test permissions related issues is to use an API key of an Administrator user in the EclecticIQ Intelligence Center versus a non-Administrator. If the Administrator sees observables in QRadar, yet the other user does not, it is 99% likely permissions are incorrectly configured.

## 1.3.1 Observable download behaviour

The current application flow is:

1. Download entities that belong to datasets (specified in feed)
2. Get observables related to entities identified at step 1

Currently the EclecticIQ v1 API does not support filtering of observables by dataset. This means that all observables linked to an entity in a datatset are currently downloaded by QRadar. 

EclecticIQ is working on an update to support filtering of observables by dataset so that only observables belonginging to specific datasets are downloaded. You can track the implementation of this here: https://ideas.eclecticiq.com/ideas/IDEA-I-1159

### 1.2.2 QRadar 

#### Step 1. Download the QRadar App from XForce

https://exchange.xforce.ibmcloud.com/hub/extension/3107d1fd9bbe8d3dfc07bd52b8b381fd

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

User can Verify the data in the reference table. The Reference Data Management app can be downloaded and installed from https://exchange.xforce.ibmcloud.com/hub/extension/074f919060a2f2dea33e365fc0c5e039.

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

# 7. Sighting Creation from offenses

Note: Rules on reference sets over 20K in size can get slow.

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
5. Filtering on network or logsource is strongly recommended, as otherwise the Rule can be slow. For example,To add the filter of logsource:
	* Locate `when the event(s) were detected by one or more of these log sources`.
	* Assign values to place holders by clicking on the following underlined parameters:
	Click these log sources > Select a log source and click 'Add' > Submit. This creates rule for matching when events are detected by one or more given log sources.
6. Click Next.
7. Select the checkbox for “Ensure the detected event is part of an offense”
	* Select  ”Index offense based on” according to the fields on rule is created. For example if a rule is created for matching Destination IP select Destination IP. 
	*”Annotate this offense” is optional. User can select and add annotations or text explaining the offense. 
	*”Include detected events by Destination IP from this point forward, in the offense, for ” is also optional. User can mention time interval in seconds to include detected events in offense.
8. Click Finish.
9. To create the sighting once the offense is created by rule,
	1. User can go to Offenses > All Offenses and can View offenses with one of the selected      Option: 	All offsenses
	2. Click on any offense.
	3. Right click on the IP address > Create EclecticIQ Sighting
	4. A pop-up window will appear to ask for the details below. 

	Clicking on save will create sightings in the EIQ platform with provided details.

	* Sighting Value: Value which is clicked
	* Sighting type: Type of sighting. Possible values: ip, domain, url, email, hash
	* Sighting title: Title of sighting
	* Sighting description: Description of sighting
	* Sighting confidence: Confidence of sighting. Possible values: low, medium, high
	* Sighting tags delimited by a comma: Any tags to attach with sighting



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
