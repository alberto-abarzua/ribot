export function prefillGoogleForm(jsonData) {
    let jsonString = JSON.stringify(jsonData);
    let encodedJsonString = encodeURIComponent(jsonString);

    // Construct the base URL of your Google Form
    let formBaseUrl =
        'https://docs.google.com/forms/d/e/1FAIpQLSdcSOAH0JEWkL2TP8eC6fkEzx7mCjZ76DKo00T4lKSs6eh1Tg/viewform?usp=pp_url';

    // Append the prefill parameter for your specific field
    let prefillParam = '&entry.604922767=' + encodedJsonString;

    // Combine the base URL with the prefill parameter
    let prefillUrl = formBaseUrl + prefillParam;

    // Open the pre-filled form in a new window or tab
    window.open(prefillUrl, '_blank');
    return prefillUrl;
}
