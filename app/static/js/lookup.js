function obs_lookup(result) {
	// Initialise app ID
	var app_id = ""
	var search_value= ""

	if (result) {
		app_id = encodeURI(result.app_id)
		search_value = encodeURI(result.search_value)
	}

	if(app_id && search_value)
	{
		// If the app ID and IP address aren't null/undefined/empty
		// Open the right click sample app in a new window
		QRadar.windowOrTab("plugins/" + app_id + "/app_proxy/lookup_observables?search_value=" + search_value);
	}

	console.log("Executed Lookup action");
	console.log(result)
}

function create_sighting(result) {
	// Initialise app ID
	var app_id = ""
	var sightings_value= ""

	if (result) {
		app_id = encodeURI(result.app_id)
		sightings_value = encodeURI(result.sightings_value)
	}

	if(app_id && sightings_value)
	{
		QRadar.windowOrTab("plugins/" + app_id + "/app_proxy/create_sighting?sighting_value=" + sightings_value);
	}

	console.log("Executed Create Sighting right click action");
	console.log(result)
}
