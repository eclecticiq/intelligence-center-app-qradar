# EclecticIQ Intelligence Center QRadar App

## App Features

* The EclecticIQ app for Qradar will collect the observables data from the EclecticIQ platform and store it in Qradar reference tables. 
* Users will be provided an option for sighting creation by right clicking on the events in the Log Activity and Offenses tab of Qradar.
* Users will be provided with an option to attach the custom action to create sighting. This action can be attached while creating custom rules in Qradar. 
* Users will be provided an option to lookup observables  by right clicking on the events in the Log Activity and Offenses tab of Qradar.
* Dashboard will be provided with below three widgets
	* Sightings by time (histogram) 
	* Sighting by Confidence (bar chart) 
	* Sighting by type count (bar chart) 

## EclecticIQ Overview

* EclecticIQ Intelligence Center is the threat intelligence solution that unites machine-powered threat data processing and dissemination with human-led data analysis without compromising analyst control, freedom or flexibility.
* EclecticIQ Intelligence Center consolidates vast amounts of internal and external structured and unstructured threat data in diverse formats from open sources, commercial suppliers, and industry partnerships. This data becomes a collaborative, contextual intelligence source of truth.
* EclecticIQ data processing pipeline ingests, normalizes, transforms, and enriches this incoming threat data into a complex, and flexible data structure. Next, our technology optimizes and prioritizes this data to help identify the most critical threats more rapidly.
* For total flexibility, EclecticIQ Intelligence Center disseminates intelligence as reports for stakeholders or as machine-readable feeds that integrate with third-party controls to improve detection, hunting, and response.
* EclecticIQ Intelligence Center offers cloud-like scalability and cost-effectiveness within your trusted environment.

## Installation

### Create a build file

1. Select `app`, `container` directory, and `manifest.json` file.
2. Zip above directories and files together in a a file `<4 digit number>`. e.g. `1952.zip`
3. Open `extension.xml` file.
4. In `application_zip` XML tag, change the `filedata` tag value to match to the zip file, e.g.

   ```xml
   <filedata>extension/1952.zip</filedata>
   ```
5. Change the `id` tag value in `application_zip` to match to the zip file. E.g.
   ```xml
   <id>/store/qapp/1952/1952.zip</id>
   ```
6. Create Directory name matching with `filedata` tag value. E.g. `EclecticIQ_1.0.0`.
7. Copy zipped file in this directory.
8. Select directory created in step `6` above, `extension.xml` and `manifest.txt` file.
9. Create a new Zip filed with name matching the directory name created in step `6` above. E.g. `extension.zip`