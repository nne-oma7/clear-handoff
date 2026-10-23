const trackForm = document.getElementById("track-form");
const trackError = document.getElementById("track-error");
const trackButton = document.getElementById("track-button");
const trackButtonLabel = document.getElementById("track-button-label");
const trackResult = document.getElementById("track-result");


function showTrackError(message) {
    trackError.textContent = message;
    trackError.hidden = false;
}


trackForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    trackError.hidden = true;
    trackResult.hidden = true;

    trackButton.disabled = true;
    trackButtonLabel.textContent = "Checking...";

    try {
        const response = await fetch("/track/lookup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                reference: document.getElementById("track-reference").value,
                contact: document.getElementById("track-contact").value
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                typeof result.detail === "string"
                    ? result.detail
                    : "Please check the details you entered."
            );
        }

        document.getElementById("track-status-label").textContent =
            result.status_label;
        document.getElementById("track-result-reference").textContent =
            result.reference;
        document.getElementById("track-message").textContent =
            result.message;
        document.getElementById("track-date").textContent =
            `Submitted ${new Date(result.submitted_at).toLocaleString()}`;

        trackResult.hidden = false;

    } catch (error) {
        showTrackError(
            error.message || "Something went wrong. Please try again."
        );
    } finally {
        trackButton.disabled = false;
        trackButtonLabel.textContent = "Check status";
    }
});